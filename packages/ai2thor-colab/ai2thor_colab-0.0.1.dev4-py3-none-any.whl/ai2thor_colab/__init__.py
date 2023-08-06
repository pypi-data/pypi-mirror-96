from IPython.display import HTML, display
import sys

import imageio

# this has no cost when ffmpeg is already downloaded, but
# it prevents moviepy from displaying an annoying message
saved_stdout = sys.stdout
with open("/dev/null", "w") as f:
    sys.stdout = f
    imageio.plugins.ffmpeg.download()
sys.stdout = saved_stdout

from moviepy.editor import ImageSequenceClip
from typing import Sequence
import numpy as np
import os

import matplotlib.pyplot as plt
import ai2thor.server

import seaborn as sns

sns.set_theme()


__version__ = "testing"


def plot_frames(event: ai2thor.server.Event) -> plt.Axes:
    frames = dict()
    third_person_frames = event.third_party_camera_frames
    if event.frame is not None:
        frames["RGB"] = event.frame
    if event.instance_segmentation_frame is not None:
        frames["Instance Segmentation"] = event.instance_segmentation_frame
    if event.semantic_segmentation_frame is not None:
        frames["Semantic Segmentation"] = event.semantic_segmentation_frame
    if event.normals_frame is not None:
        frames["Normals"] = event.normals_frame
    if event.depth_frame is not None:
        frames["Depth"] = event.depth_frame

    if len(frames) == 0:
        raise Exception("No agent frames rendered on this event!")

    rows = 2 if len(third_person_frames) else 1
    cols = max(len(frames), len(third_person_frames))
    fig, axs = plt.subplots(
        nrows=rows, ncols=cols, dpi=150, figsize=(3 * cols, 3 * rows)
    )

    agent_row = axs[0] if rows > 1 else axs

    for i, (name, frame) in enumerate(frames.items()):
        ax = agent_row[i] if cols > 1 else agent_row
        im = ax.imshow(frame)
        ax.axis("off")
        ax.set_title(name)

        if name == "Depth":
            fig.colorbar(im, fraction=0.046, pad=0.04, ax=ax)

    # set unused axes off
    for i in range(len(frames), cols):
        agent_row[i].axis("off")

    # add third party camera frames
    if rows > 1:
        for i, frame in enumerate(third_person_frames):
            ax = axs[1][i] if cols > 1 else axs[1]
            ax.imshow(frame)
            ax.axis("off")
        for i in range(len(third_person_frames), cols):
            axs[1][i].axis("off")

        fig.text(x=0.1, y=0.715, s="Agent Frames", rotation="vertical", va="center")
        fig.text(
            x=0.1, y=0.3025, s="Third Person Frames", rotation="vertical", va="center"
        )


def show_video(frames: Sequence[np.ndarray], fps: int = 10):
    """Show a video composed of a sequence of frames."""
    frames = ImageSequenceClip(frames, fps=fps)
    return frames.ipython_display()


def start_xserver():
    """Provide the ability to render AI2-THOR using Google Colab."""

    def progress(value):
        return HTML(
            f"""
            <progress value='{value}' max="100", style='width: 100%'>
                {value}
            </progress>
        """
        )

    progress_bar = display(progress(0), display_id=True)

    try:
        import google.colab

        using_colab = True
    except ImportError:
        using_colab = False

    if using_colab:
        with open("frame-buffer", "w") as writefile:
            writefile.write(
                """#taken from https://gist.github.com/jterrace/2911875
        XVFB=/usr/bin/Xvfb
        XVFBARGS=":1 -screen 0 1024x768x24 -ac +extension GLX +render -noreset"
        PIDFILE=./frame-buffer.pid
        case "$1" in
        start)
            /sbin/start-stop-daemon --start --quiet --pidfile $PIDFILE --make-pidfile --background --exec $XVFB -- $XVFBARGS
            ;;
        stop)
            /sbin/start-stop-daemon --stop --quiet --pidfile $PIDFILE
            rm $PIDFILE
            ;;
        restart)
            $0 stop
            $0 start
            ;;
        *)
                exit 1
        esac
        exit 0
            """
            )

        progress_bar.update(progress(5))
        os.system("apt-get install daemon >/dev/null 2>&1")

        progress_bar.update(progress(10))
        os.system("apt-get install wget >/dev/null 2>&1")

        progress_bar.update(progress(20))
        os.system(
            "wget http://security.ubuntu.com/ubuntu/pool/main/libx/libxfont/libxfont1_1.5.1-1ubuntu0.16.04.4_amd64.deb >/dev/null 2>&1"
        )

        progress_bar.update(progress(30))
        os.system(
            "wget --output-document xvfb.deb http://security.ubuntu.com/ubuntu/pool/universe/x/xorg-server/xvfb_1.18.4-0ubuntu0.11_amd64.deb >/dev/null 2>&1"
        )

        progress_bar.update(progress(40))
        os.system("dpkg -i libxfont1_1.5.1-1ubuntu0.16.04.4_amd64.deb >/dev/null 2>&1")

        progress_bar.update(progress(50))
        os.system("dpkg -i xvfb.deb >/dev/null 2>&1")

        progress_bar.update(progress(70))
        os.system("rm libxfont1_1.5.1-1ubuntu0.16.04.4_amd64.deb")

        progress_bar.update(progress(80))
        os.system("rm xvfb.deb")

        progress_bar.update(progress(90))
        os.system("bash frame-buffer start")

        os.environ["DISPLAY"] = ":1"
    progress_bar.update(progress(100))
