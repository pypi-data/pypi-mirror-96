"""
Main module for truckersmp-cli main script.

Licensed under MIT.
"""

import json
import logging
import os
import signal
import subprocess as subproc
import sys

from .args import check_args_errors, create_arg_parser
from .steamcmd import update_game
from .truckersmp import update_mod
from .utils import (
    activate_native_d3dcompiler_47, check_libsdl2,
    perform_self_update, set_wine_desktop_registry,
    start_wine_discord_ipc_bridge, wait_for_steam,
)
from .variables import AppId, Args, Dir, File, URL

PKG_RESOURCES_IS_AVAILABLE = False
try:
    import pkg_resources
    PKG_RESOURCES_IS_AVAILABLE = True
except ImportError:
    pass


def get_version_string():
    """
    Get the version of this program and return it in string format.

    This first tries to load "RELEASE" file
    for GitHub release assets or cloned git repo directory.
    If succeeded, it additionally tries to get git commit hash and append it.
    Otherwise, it tries to get version from Python package
    only when "pkg_resources" module is available.
    If the version is still unknown, this returns "unknown".
    """
    version = ""
    try:
        # try to load "RELEASE" file for release assets or cloned git directory
        with open(os.path.join(os.path.dirname(Dir.scriptdir), "RELEASE")) as f_in:
            version += f_in.readline().rstrip()
    except OSError:
        pass
    if version:
        try:
            # try to get git commit hash, and append it if succeeded
            version += subproc.check_output(
                ("git", "log", "-1", "--format= (%h)")).decode("utf-8").rstrip()
        except (OSError, subproc.CalledProcessError):
            pass
    else:
        # try to get version from Python package
        try:
            if PKG_RESOURCES_IS_AVAILABLE:
                version += pkg_resources.get_distribution(__package__).version
        except pkg_resources.DistributionNotFound:
            pass
    return version if version else "unknown"


def main():
    """truckersmp-cli main function."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # load Proton AppID info from "proton.json":
    #     {"X.Y": AppID, ... , "default": "X.Y"}
    # example:
    #     {"5.0": 1245040, "4.11": 1113280, "default": "5.0"}
    try:
        with open(File.proton_json) as f_in:
            AppId.proton = json.load(f_in)
    except (OSError, ValueError) as ex:
        sys.exit("Failed to load proton.json: {}".format(ex))

    # parse options
    arg_parser = create_arg_parser()
    arg_parser.parse_args(namespace=Args)

    # print version
    if Args.version:
        print(get_version_string())
        sys.exit()

    # check whether the executable of our inject program is present
    if not os.access(File.inject_exe, os.R_OK):
        sys.exit("""DLL inject program ("{}") is missing.

Try one of the following:
* Install truckersmp-cli via pip [RECOMMENDED]
  (e.g. "python3 -m pip install --user truckersmp-cli[optional]")
  and run it (e.g. "~/.local/bin/truckersmp-cli [ARGUMENTS...]")
* Download GitHub release file from "{}", unpack it, and run
  the "truckersmp-cli" script in the unpacked directory
* Build "truckersmp-cli.exe" with mingw-w64, put it into "{}",
  and run this script again

See {} for additional information.""".format(
            File.inject_exe, URL.project_releases, Dir.scriptdir, URL.project_doc_inst))

    # set up logging
    setup_logging()

    # self update
    if Args.self_update:
        perform_self_update()
        sys.exit()

    # fallback to old local folder
    if not Args.moddir:
        old_local_moddir = os.path.join(Dir.scriptdir, "truckersmp")
        if (os.path.isdir(old_local_moddir)
                and os.access(old_local_moddir, os.R_OK | os.W_OK | os.X_OK)):
            logging.debug("No moddir set and fallback found")
            Args.moddir = old_local_moddir
        else:
            logging.debug("No moddir set, setting to default")
            Args.moddir = Dir.default_moddir
    logging.info("Mod directory: %s", Args.moddir)

    # check for errors
    check_args_errors()

    # download/update ATS/ETS2 and Proton
    if Args.update:
        logging.debug("Updating game files")
        update_game()

    # update truckersmp when starting multiplayer
    if not Args.singleplayer:
        logging.debug("Updating mod files")
        update_mod()

    # start truckersmp with proton or wine
    if Args.start:
        # check for Proton availability when starting with Proton
        if (Args.proton
                and not os.access(os.path.join(Args.protondir, "proton"), os.R_OK)):
            sys.exit("""Proton is not found in {}
Run with '--update' option to install Proton""".format(Args.protondir))

        if not check_libsdl2():
            sys.exit("SDL2 was not found on your system.")
        start_functions = (("Proton", start_with_proton), ("Wine", start_with_wine))
        i = 0 if Args.proton else 1
        compat_tool, start_game = start_functions[i]
        logging.debug("Starting game with %s", compat_tool)
        start_game()

    sys.exit()


def setup_logging():
    """
    Set up Python logging facility.

    This function must be called after parse_args().
    """
    formatter = logging.Formatter("** {levelname} **  {message}", style="{")
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)
    logger = logging.getLogger()
    if Args.verbose:
        logger.setLevel(logging.INFO if Args.verbose == 1 else logging.DEBUG)
    logger.addHandler(stderr_handler)
    if Args.logfile != "":
        file_handler = logging.FileHandler(Args.logfile, mode="w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def start_with_proton():
    """Start game with Proton."""
    # pylint: disable=too-many-branches,too-many-statements
    steamdir = wait_for_steam(use_proton=True, loginvdf_paths=File.loginusers_paths)
    logging.info("Steam installation directory: %s", steamdir)

    logging.debug("Creating directory %s if it doesn't exist", Args.prefixdir)
    os.makedirs(Args.prefixdir, exist_ok=True)

    prefix = os.path.join(Args.prefixdir, "pfx")
    proton = os.path.join(Args.protondir, "proton")
    argv = [sys.executable, proton, "run"]
    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = Args.prefixdir
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = steamdir

    # Proton's "dist" directory tree is missing until first run
    # make sure it's present for using "dist/bin/wine" directly
    wine = os.path.join(Args.protondir, "dist/bin/wine")
    if (not os.access(wine, os.R_OK)
            # native d3dcompiler_47 is removed when the prefix is downgraded
            # make sure the prefix is already upgraded/downgraded
            or Args.activate_native_d3dcompiler_47):
        try:
            subproc.check_output(
                argv + ["wineboot", ], env=env, stderr=subproc.STDOUT)
        except OSError as ex:
            sys.exit("Failed to run wineboot: {}".format(ex))
        except subproc.CalledProcessError as ex:
            sys.exit("wineboot failed:\n{}".format(ex.output.decode("utf-8")))

    # activate native d3dcompiler_47
    if Args.activate_native_d3dcompiler_47:
        activate_native_d3dcompiler_47(prefix, wine)

    # enable Wine desktop if requested
    if Args.wine_desktop:
        set_wine_desktop_registry(prefix, wine, True)

    env["PROTON_USE_WINED3D"] = "1" if Args.use_wined3d else "0"
    env["PROTON_NO_D3D11"] = "1" if not Args.enable_d3d11 else "0"
    # enable Steam Overlay unless "--disable-proton-overlay" is specified
    if Args.disable_proton_overlay:
        ld_preload = ""
    else:
        overlayrenderer = os.path.join(steamdir, File.overlayrenderer_inner)
        if "LD_PRELOAD" in env:
            env["LD_PRELOAD"] += ":" + overlayrenderer
        else:
            env["LD_PRELOAD"] = overlayrenderer
        ld_preload = "LD_PRELOAD={}\n  ".format(env["LD_PRELOAD"])

    # start wine-discord-ipc-bridge for multiplayer
    # unless "--without-wine-discord-ipc-bridge" is specified
    ipcbr_proc = None
    if not Args.singleplayer and not Args.without_wine_discord_ipc_bridge:
        ipcbr_proc = start_wine_discord_ipc_bridge(argv, env)

    # check whether singleplayer or multiplayer
    if Args.singleplayer:
        exename = "eurotrucks2.exe" if Args.ets2 else "amtrucks.exe"
        gamepath = os.path.join(Args.gamedir, "bin/win_x64", exename)
        argv += gamepath, "-nointro", "-64bit"
    else:
        argv += File.inject_exe, Args.gamedir, Args.moddir

    env["SteamGameId"] = Args.steamid
    env["SteamAppId"] = Args.steamid
    logging.info(
        """Startup command:
  SteamGameId=%s
  SteamAppId=%s
  STEAM_COMPAT_DATA_PATH=%s
  STEAM_COMPAT_CLIENT_INSTALL_PATH=%s
  PROTON_USE_WINED3D=%s
  PROTON_NO_D3D11=%s
  %s%s %s
  run
  %s %s %s""",
        env["SteamGameId"], env["SteamAppId"],
        env["STEAM_COMPAT_DATA_PATH"], env["STEAM_COMPAT_CLIENT_INSTALL_PATH"],
        env["PROTON_USE_WINED3D"],
        env["PROTON_NO_D3D11"],
        ld_preload,
        sys.executable, proton, argv[-3], argv[-2], argv[-1])
    try:
        output = subproc.check_output(argv, env=env, stderr=subproc.STDOUT)
        logging.info("Proton output:\n%s", output.decode("utf-8"))
    except subproc.CalledProcessError as ex:
        logging.error("Proton output:\n%s", ex.output.decode("utf-8"))

    if ipcbr_proc:
        # make sure wine-discord-ipc-bridge is exited
        if ipcbr_proc.poll() is None:
            ipcbr_proc.kill()
        ipcbr_proc.wait()

    # disable Wine desktop if enabled
    if Args.wine_desktop:
        set_wine_desktop_registry(prefix, wine, False)


def start_with_wine():
    """Start game with Wine."""
    wine = os.environ["WINE"] if "WINE" in os.environ else "wine"
    if Args.activate_native_d3dcompiler_47:
        activate_native_d3dcompiler_47(Args.prefixdir, wine)

    env = os.environ.copy()
    env["WINEDEBUG"] = "-all"
    env["WINEARCH"] = "win64"
    env["WINEPREFIX"] = Args.prefixdir

    wait_for_steam(
        use_proton=False,
        loginvdf_paths=(os.path.join(Args.wine_steam_dir, File.loginvdf_inner), ),
        wine=wine,
        env=env,
    )

    argv = [wine, ]

    ipcbr_proc = None
    if not Args.singleplayer and not Args.without_wine_discord_ipc_bridge:
        ipcbr_proc = start_wine_discord_ipc_bridge(argv, env)

    if "WINEDLLOVERRIDES" not in env:
        env["WINEDLLOVERRIDES"] = ""
    if not Args.enable_d3d11:
        env["WINEDLLOVERRIDES"] += ";d3d11=;dxgi="

    desktop_args = ""
    if Args.wine_desktop:
        argv += "explorer", "/desktop=TruckersMP,{}".format(Args.wine_desktop)
        desktop_args += argv[1] + " " + argv[2] + " "
    if Args.singleplayer:
        exename = "eurotrucks2.exe" if Args.ets2 else "amtrucks.exe"
        gamepath = os.path.join(Args.gamedir, "bin/win_x64", exename)
        argv += gamepath, "-nointro", "-64bit"
    else:
        argv += File.inject_exe, Args.gamedir, Args.moddir
    logging.info(
        """Startup command:
  WINEDEBUG=-all
  WINEARCH=win64
  WINEPREFIX=%s
  WINEDLLOVERRIDES="%s"
  %s %s%s %s %s""",
        env["WINEPREFIX"], env["WINEDLLOVERRIDES"],
        wine, desktop_args, argv[-3], argv[-2], argv[-1])
    try:
        output = subproc.check_output(argv, env=env, stderr=subproc.STDOUT)
        logging.info("Wine output:\n%s", output.decode("utf-8"))
    except subproc.CalledProcessError as ex:
        logging.error("Wine output:\n%s", ex.output.decode("utf-8"))

    if ipcbr_proc:
        if ipcbr_proc.poll() is None:
            ipcbr_proc.kill()
        ipcbr_proc.wait()
