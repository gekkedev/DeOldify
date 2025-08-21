from fastai.core import *
from fastai.vision import *
from matplotlib.axes import Axes
from .filters import IFilter, MasterFilter, ColorizerFilter
from .generators import gen_inference_deep, gen_inference_wide
from .render_factor import guess_render_factor
from PIL import Image
import ffmpeg
import gc
import requests
from io import BytesIO
import base64
from IPython import display as ipythondisplay
from IPython.display import HTML
from IPython.display import Image as ipythonimage
import cv2
import logging
from fastprogress.fastprogress import progress_bar, MasterBar
from fastai.basic_data import DatasetType
import torch
from typing import List
from deoldify import device

# adapted from https://www.pyimagesearch.com/2016/04/25/watermarking-images-with-opencv-and-python/
def get_watermarked(pil_image: Image) -> Image:
    try:
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        (h, w) = image.shape[:2]
        image = np.dstack([image, np.ones((h, w), dtype="uint8") * 255])
        pct = 0.05
        full_watermark = cv2.imread(
            './resource_images/watermark.png', cv2.IMREAD_UNCHANGED
        )
        (fwH, fwW) = full_watermark.shape[:2]
        wH = int(pct * h)
        wW = int((pct * h / fwH) * fwW)
        watermark = cv2.resize(full_watermark, (wH, wW), interpolation=cv2.INTER_AREA)
        overlay = np.zeros((h, w, 4), dtype="uint8")
        (wH, wW) = watermark.shape[:2]
        overlay[h - wH - 10 : h - 10, 10 : 10 + wW] = watermark
        # blend the two images together using transparent overlays
        output = image.copy()
        cv2.addWeighted(overlay, 0.5, output, 1.0, 0, output)
        rgb_image = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        final_image = Image.fromarray(rgb_image)
        return final_image
    except:
        # Don't want this to crash everything, so let's just not watermark the image for now.
        return pil_image


class ModelImageVisualizer:
    def __init__(self, filter: IFilter, results_dir: str = None):
        self.filter = filter
        self.results_dir = None if results_dir is None else Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _clean_mem(self):
        torch.cuda.empty_cache()
        # gc.collect()

    def _open_pil_image(self, path: Path) -> Image:
        return PIL.Image.open(path).convert('RGB')

    def _get_image_from_url(self, url: str) -> Image:
        response = requests.get(url, timeout=30, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'})
        img = PIL.Image.open(BytesIO(response.content)).convert('RGB')
        return img

    def plot_transformed_image_from_url(
        self,
        url: str,
        path: str = 'test_images/image.png',
        results_dir:Path = None,
        figsize: Tuple[int, int] = (20, 20),
        render_factor: int = None,
        
        display_render_factor: bool = False,
        compare: bool = False,
        post_process: bool = True,
        watermarked: bool = True,
    ) -> Path:
        img = self._get_image_from_url(url)
        img.save(path)
        return self.plot_transformed_image(
            path=path,
            results_dir=results_dir,
            figsize=figsize,
            render_factor=render_factor,
            display_render_factor=display_render_factor,
            compare=compare,
            post_process = post_process,
            watermarked=watermarked,
        )

    def plot_transformed_image(
        self,
        path: str,
        results_dir:Path = None,
        figsize: Tuple[int, int] = (20, 20),
        render_factor: int = None,
        display_render_factor: bool = False,
        compare: bool = False,
        post_process: bool = True,
        watermarked: bool = True,
    ) -> Path:
        path = Path(path)
        if results_dir is None:
            results_dir = Path(self.results_dir)
        result = self.get_transformed_image(
            path, render_factor, post_process=post_process,watermarked=watermarked
        )
        orig = self._open_pil_image(path)
        if compare:
            self._plot_comparison(
                figsize, render_factor, display_render_factor, orig, result
            )
        else:
            self._plot_solo(figsize, render_factor, display_render_factor, result)

        orig.close()
        result_path = self._save_result_image(path, result, results_dir=results_dir)
        result.close()
        return result_path

    def _plot_comparison(
        self,
        figsize: Tuple[int, int],
        render_factor: int,
        display_render_factor: bool,
        orig: Image,
        result: Image,
    ):
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        self._plot_image(
            orig,
            axes=axes[0],
            figsize=figsize,
            render_factor=render_factor,
            display_render_factor=False,
        )
        self._plot_image(
            result,
            axes=axes[1],
            figsize=figsize,
            render_factor=render_factor,
            display_render_factor=display_render_factor,
        )

    def _plot_solo(
        self,
        figsize: Tuple[int, int],
        render_factor: int,
        display_render_factor: bool,
        result: Image,
    ):
        fig, axes = plt.subplots(1, 1, figsize=figsize)
        self._plot_image(
            result,
            axes=axes,
            figsize=figsize,
            render_factor=render_factor,
            display_render_factor=display_render_factor,
        )

    def _save_result_image(self, source_path: Path, image: Image, results_dir = None) -> Path:
        if results_dir is None:
            results_dir = Path(self.results_dir)
        result_path = results_dir / source_path.name
        image.save(result_path)
        return result_path

    def get_transformed_image(
        self, path: Path, render_factor: int = None, post_process: bool = True,
        watermarked: bool = True,
    ) -> Image:
        self._clean_mem()
        orig_image = self._open_pil_image(path)
        filtered_image = self.filter.filter(
            orig_image, orig_image, render_factor=render_factor,post_process=post_process
        )

        if watermarked:
            return get_watermarked(filtered_image)

        return filtered_image

    def _plot_image(
        self,
        image: Image,
        render_factor: int,
        axes: Axes = None,
        figsize=(20, 20),
        display_render_factor = False,
    ):
        if axes is None:
            _, axes = plt.subplots(figsize=figsize)
        axes.imshow(np.asarray(image) / 255)
        axes.axis('off')
        if render_factor is not None and display_render_factor:
            plt.text(
                10,
                10,
                'render_factor: ' + str(render_factor),
                color='white',
                backgroundcolor='black',
            )

    def _get_num_rows_columns(self, num_images: int, max_columns: int) -> Tuple[int, int]:
        columns = min(num_images, max_columns)
        rows = num_images // columns
        rows = rows if rows * columns == num_images else rows + 1
        return rows, columns


class VideoColorizer:
    def __init__(self, vis: ModelImageVisualizer):
        self.vis = vis
        workfolder = Path('./video')
        self.source_folder = workfolder / "source"
        self.bwframes_root = workfolder / "bwframes"
        self.audio_root = workfolder / "audio"
        self.colorframes_root = workfolder / "colorframes"
        self.result_folder = workfolder / "result"

    def _get_ffmpeg_probe(self, path:Path):
        try:
            probe = ffmpeg.probe(str(path))
            return probe
        except ffmpeg.Error as e:
            logging.error("ffmpeg error: {0}".format(e), exc_info=True)
            logging.error('stdout:' + e.stdout.decode('UTF-8'))
            logging.error('stderr:' + e.stderr.decode('UTF-8'))
            raise e
        except Exception as e:
            logging.error('Failed to instantiate ffmpeg.probe.  Details: {0}'.format(e), exc_info=True)   
            raise e

    def _get_fps(self, source_path: Path) -> str:
        probe = self._get_ffmpeg_probe(source_path)
        stream_data = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
            None,
        )
        return stream_data['avg_frame_rate']

    def _extract_raw_frames(self, source_path: Path):
        bwframes_folder = self.bwframes_root / (source_path.stem)
        bwframe_path_template = str(bwframes_folder / '%5d.jpg')
        bwframes_folder.mkdir(parents=True, exist_ok=True)
        colorframes_folder = self.colorframes_root / (source_path.stem)

        # Skip extraction when B&W frames already exist so interrupted runs can resume.
        # The assumption that **all** B&W frames were already extracted is derived from the existence of any colored frames, indicating that the B&W extraction was completed.
        if any(bwframes_folder.glob('*.jpg')) and any(colorframes_folder.glob('*.jpg')):
            return print(
                f"Skipping extraction of B&W frames (already existing)."
            )
        logging.info(f"Extracting raw frames from {source_path} to {bwframes_folder}")

        process = (
            ffmpeg
                .input(str(source_path))
                .output(str(bwframe_path_template), format='image2', vcodec='mjpeg', **{'q:v':'0'})
                .global_args('-hide_banner')
                .global_args('-nostats')
                .global_args('-loglevel', 'error')
        )

        try:
            process.run()
        except ffmpeg.Error as e:
            logging.error("ffmpeg error: {0}".format(e), exc_info=True)
            logging.error('stdout:' + e.stdout.decode('UTF-8'))
            logging.error('stderr:' + e.stderr.decode('UTF-8'))
            raise e
        except Exception as e:
            logging.error('Errror while extracting raw frames from source video.  Details: {0}'.format(e), exc_info=True)
            raise e

    def _colorize_raw_frames(
        self, source_path: Path, render_factor: int = None, post_process: bool = True,
        watermarked: bool = True, bar: MasterBar = None
    ):
        colorframes_folder = self.colorframes_root / (source_path.stem)
        colorframes_folder.mkdir(parents=True, exist_ok=True)
        existing_color_frames = {f.name for f in colorframes_folder.glob('*.jpg')}
        color_count = len(existing_color_frames)

        bwframes_folder = self.bwframes_root / (source_path.stem)
        bw_images = os.listdir(str(bwframes_folder))
        bw_count = len(bw_images)

        if color_count == bw_count:
            return print(f"Skipping colorization of {source_path.stem} because all {color_count} frames are already colorized.")

        if len(existing_color_frames) > 0:
            print(str(color_count) + " existing frames (of " + str(bw_count) + ") found that were already colorized.")

        if render_factor is None:
            # If no render_factor is provided, estimate it based on any B/W frame.
            if bw_count == 0:
                print(f"No B/W frames found in {bwframes_folder}. Using default render_factor.")
                render_factor = 21
            else:
                print(f"Estimating render_factor from existing B/W frames in {bwframes_folder}.")
                # Use the first B/W frame to guess a good render_factor
            render_factor = guess_render_factor(str(bwframes_folder / bw_images[0]))
            print(f"Using a render_factor based on existing B/W frames.")
        print(f"Colorizing {bw_count - color_count} frames with render_factor={render_factor}...")

        color_filter = self.vis.filter.filters[0]
        render_sz = render_factor * color_filter.render_base

        def estimate_batch_size() -> int:
            """Estimate a starting batch size from resolution and memory.

            batch_size ≈ target_mem / (render_sz**2 * channels * dtype)
            where target_mem is 50% of GPU RAM or 25% of system RAM on CPU.
            """
            frame_bytes = render_sz * render_sz * 3 * 4  # 3 channels, float32
            if device.backend() == "cuda":
                total = torch.cuda.get_device_properties(0).total_memory
                target = total * 0.5
            elif device.backend() == "cpu":
                try:
                    import psutil
                    total = psutil.virtual_memory().available
                    target = total * 0.25
                except Exception:
                    # Fallback for systems without psutil
                    target = 512 * 1024 ** 2
            else:
                # DirectML or other backends don't expose memory; assume ~1GB
                target = 1 * 1024 ** 3
            # Cap at 32 to avoid runaway allocations; OOM handler will scale down.
            return max(1, min(32, int(target / frame_bytes)))

        batch_size = estimate_batch_size()
        batch_files: List[str] = []

        # Move the model and learner to the selected backend and keep track of it
        # so that `pred_batch` doesn't bounce tensors across devices.
        torch_dev = device.torch_device()
        color_filter.learn.model.to(torch_dev)
        color_filter.learn.data.device = torch_dev
        color_filter.device = torch_dev

        def process_batch(files: List[str]):
            """Colorize a single batch of frame files."""
            nonlocal batch_size
            if not files:
                return

            origs, tensors = [], []
            for name in files:
                img_path = bwframes_folder / name
                orig = Image.open(img_path).convert('RGB')
                filt = color_filter._transform(orig)
                model_ready = color_filter._get_model_ready_image(filt, render_sz)
                t = pil2tensor(model_ready, np.float32)
                # Keep preprocessing on CPU to avoid unsupported DirectML ops
                t.div_(255)
                t, _ = color_filter.norm((t, t), do_x=True)
                origs.append(orig)
                tensors.append(t)

            # Stack then ship the entire batch to the model's device once
            batch = torch.stack(tensors).to(color_filter.device, non_blocking=True)
            # Some layers (e.g. spectral norm) may sneak weights back to CPU when
            # using DirectML, so reassert the model on the target device here.
            color_filter.learn.model.to(color_filter.device)
            try:
                preds = color_filter.learn.pred_batch(
                    ds_type=DatasetType.Valid, batch=(batch, batch), reconstruct=True
                )
            except RuntimeError as e:
                msg = str(e).lower()
                oom_signals = ["out of memory", "unbox expects dml", "privateuse1"]
                if any(sig in msg for sig in oom_signals) and len(files) > 1:
                    # Free cached memory and retry with a smaller batch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    gc.collect()
                    batch_size = max(1, batch_size // 2)
                    print(f"OOM detected, reducing batch size to {batch_size}")
                    # Drop the current batch before recursion to release memory
                    del batch
                    for i in range(0, len(files), batch_size):
                        process_batch(files[i : i + batch_size])
                    return
                raise

            for pred, orig, name in zip(preds, origs, files):
                out = color_filter.denorm(pred.px, do_x=False)
                out = image2np(out * 255).astype(np.uint8)
                model_img = Image.fromarray(out)
                raw = color_filter._unsquare(model_img, orig)
                result = (
                    color_filter._post_process(raw, orig) if post_process else raw
                )
                if watermarked:
                    result = get_watermarked(result)
                result.save(str(colorframes_folder / name))
                result.close()
                orig.close()

        for img in progress_bar(bw_images, master=bar):
            img_path = bwframes_folder / img
            if not img_path.is_file() or img in existing_color_frames:
                continue
            batch_files.append(img)
            if len(batch_files) == batch_size:
                process_batch(batch_files)
                batch_files = []

        if batch_files:
            process_batch(batch_files)

    def _build_video(self, source_path: Path) -> Path:
        colorized_path = self.result_folder / (
            source_path.name.replace('.mp4', '_no_audio.mp4')
        )
        colorframes_folder = self.colorframes_root / (source_path.stem)
        colorframes_path_template = str(colorframes_folder / '%5d.jpg')
        colorized_path.parent.mkdir(parents=True, exist_ok=True)
        if colorized_path.exists():
            colorized_path.unlink()
        fps = self._get_fps(source_path)

        process = (
            ffmpeg 
                .input(str(colorframes_path_template), format='image2', vcodec='mjpeg', framerate=fps) 
                .output(str(colorized_path), crf=17, vcodec='libx264')
                .global_args('-hide_banner')
                .global_args('-nostats')
                .global_args('-loglevel', 'error')
        )

        try:
            process.run()
        except ffmpeg.Error as e:
            logging.error("ffmpeg error: {0}".format(e), exc_info=True)
            logging.error('stdout:' + e.stdout.decode('UTF-8'))
            logging.error('stderr:' + e.stderr.decode('UTF-8'))
            raise e
        except Exception as e:
            logging.error('Errror while building output video.  Details: {0}'.format(e), exc_info=True)   
            raise e

        result_path = self.result_folder / source_path.name
        if result_path.exists():
            logging.info(f"Skipping reassembly of existing video: {result_path} - delete the output file if you wish to have it recreated.")
            #result_path.unlink()
        else:
            logging.info(f"Assembling video: {result_path}")
            # making copy of non-audio version in case adding back audio doesn't apply or fails.
            shutil.copyfile(str(colorized_path), str(result_path))

            # adding back sound here
            audio_file = Path(str(source_path).replace('.mp4', '.aac'))
            if audio_file.exists():
                audio_file.unlink()

            os.system(
                'ffmpeg -y -i "'
                + str(source_path)
                + '" -vn -acodec copy "'
                + str(audio_file)
                + '"'
                + ' -hide_banner'
                + ' -nostats'
                + ' -loglevel error'
            )

            if audio_file.exists():
                os.system(
                    'ffmpeg -y -i "'
                    + str(colorized_path)
                    + '" -i "'
                    + str(audio_file)
                    + '" -shortest -c:v copy -c:a aac -b:a 256k "'
                    + str(result_path)
                    + '"'
                    + ' -hide_banner'
                    + ' -nostats'
                    + ' -loglevel error'
                )
            logging.info('Video created here: ' + str(result_path))
        return result_path

    def colorize_from_file_name(
        self, file_name: str, render_factor: int = None,  watermarked: bool = True, post_process: bool = True, bar: MasterBar = None
    ) -> Path:
        source_path: Path = self.source_folder / file_name
        if not source_path.exists():
            raise Exception(
                'Video at path specfied (' + str(source_path) + ') could not be found.'
            )
        self._extract_raw_frames(source_path)
        self._colorize_raw_frames(
            source_path, render_factor=render_factor, post_process=post_process, watermarked=watermarked, bar=bar
        )
        return self._build_video(source_path)


def get_video_colorizer(render_factor: int = 21) -> VideoColorizer:
    return get_stable_video_colorizer(render_factor=render_factor)


def get_artistic_video_colorizer(
    root_folder: Path = Path('./'),
    weights_name: str = 'ColorizeArtistic_gen',
    results_dir='result_images',
    render_factor: int = 35
) -> VideoColorizer:
    learn = gen_inference_deep(root_folder=root_folder, weights_name=weights_name)
    filtr = MasterFilter([ColorizerFilter(learn=learn)], render_factor=render_factor)
    vis = ModelImageVisualizer(filtr, results_dir=results_dir)
    return VideoColorizer(vis)


def get_stable_video_colorizer(
    root_folder: Path = Path('./'),
    weights_name: str = 'ColorizeVideo_gen',
    results_dir='result_images',
    render_factor: int = 21
) -> VideoColorizer:
    learn = gen_inference_wide(root_folder=root_folder, weights_name=weights_name)
    filtr = MasterFilter([ColorizerFilter(learn=learn)], render_factor=render_factor)
    vis = ModelImageVisualizer(filtr, results_dir=results_dir)
    return VideoColorizer(vis)


def get_image_colorizer(
    root_folder: Path = Path('./'), render_factor: int = 35, artistic: bool = True
) -> ModelImageVisualizer:
    if artistic:
        return get_artistic_image_colorizer(root_folder=root_folder, render_factor=render_factor)
    else:
        return get_stable_image_colorizer(root_folder=root_folder, render_factor=render_factor)


def get_stable_image_colorizer(
    root_folder: Path = Path('./'),
    weights_name: str = 'ColorizeStable_gen',
    results_dir='result_images',
    render_factor: int = 35
) -> ModelImageVisualizer:
    learn = gen_inference_wide(root_folder=root_folder, weights_name=weights_name)
    filtr = MasterFilter([ColorizerFilter(learn=learn)], render_factor=render_factor)
    vis = ModelImageVisualizer(filtr, results_dir=results_dir)
    return vis


def get_artistic_image_colorizer(
    root_folder: Path = Path('./'),
    weights_name: str = 'ColorizeArtistic_gen',
    results_dir='result_images',
    render_factor: int = 35
) -> ModelImageVisualizer:
    learn = gen_inference_deep(root_folder=root_folder, weights_name=weights_name)
    filtr = MasterFilter([ColorizerFilter(learn=learn)], render_factor=render_factor)
    vis = ModelImageVisualizer(filtr, results_dir=results_dir)
    return vis


def show_image_in_notebook(image_path: Path):
    ipythondisplay.display(ipythonimage(str(image_path)))


def show_video_in_notebook(video_path: Path):
    video = io.open(video_path, 'r+b').read()
    encoded = base64.b64encode(video)
    ipythondisplay.display(
        HTML(
            data='''<video alt="test" autoplay 
                loop controls style="height: 400px;">
                <source src="data:video/mp4;base64,{0}" type="video/mp4" />
             </video>'''.format(
                encoded.decode('ascii')
            )
        )
    )
