#!/home/ani/miniconda3/envs/scripting/bin/python
"""
Converts image to pdf.
Author: Ani Aggarwal @https://github.com/AniAggarwal
"""
from pathlib import Path
import sys
import re
import shutil
import subprocess
import argparse

# from transform import apply_brightness_contrast

try:
    import cv2
    import img2pdf
except ImportError:
    bashCommand = "pip install opencv-python img2pdf"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)


def apply_brightness_contrast(input_img, brightness=0, contrast=0):
    # Code from @bfris at https://stackoverflow.com/a/50053219

    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf


def get_img_name(img_path):
    """
    Gets the name of the supplied file, without the suffix.

    Parameters
    ----------
    img_path: Path, a path object of the pdf output path.

    Returns
    -------
    string, the file's name wihtout the suffix. Returns None if the img_path isn't a jpg or png.
    """
    img_match = re.search("(.*)(\.png|\.jpg)$", str(img_path))
    if img_match is not None:
        return img_match.group(1)
    return None


def get_output_path(output_path):
    """
    Gets a valid output path with a correct file suffix.

    Parameters
    ----------
    output_path: Path, a path object of the pdf output path.

    Returns
    -------
    Path, the updated output path of the pdf.
    """
    return output_path.with_suffix(".pdf")


def convert_imgs(
    input_dir, output_dir=None, temp_suffix="__temp", brightness=0, contrast=0
):
    """
    Converts and stores images in given directories into images that can be proccessed and turned into a pdf.

    Parameters
    ----------
    input_dir:      string, the loctaion of input images. Must end with a /
    output_dir:     string, the location of the directory of output images. Defaulted to temp folder in input_dir.
    temp_suffix:    string, the suffix to attach to temp files created by function

    Returns
    -------
    string, the path to directory containing the converted images
    """
    if output_dir is None:
        output_dir = input_dir / ".images_to_pdf_temp"

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        user_cont = "_"
        while (
            user_cont.lower().strip() != "y"
            and user_cont.lower().strip() != "n"
            and user_cont != ""
        ):
            user_cont = input(
                f"Proceeding will overwrite the following file: {str(output_dir)}\nContinue (Y/n): "
            )
            if user_cont.lower().strip() == "n":
                print("Operation canceled.")
                exit(0)

        output_dir.unlink()
        output_dir.mkdir(parents=True)

    for img_path in input_dir.iterdir():
        img_name = get_img_name(img_path.name)  # does not included suffix

        if img_name is not None:
            img = cv2.imread(str((input_dir / img_path.name)))

            transformed_img = apply_brightness_contrast(img, brightness, contrast)

            file_name = img_name + temp_suffix + ".jpg"
            output_path = output_dir / file_name

            cv2.imwrite(str(output_path), transformed_img)

    return output_dir


def imgs_to_pdf(imgs_dir, output_path):
    imgs_paths = [str(imgs_dir / name.name) for name in imgs_dir.iterdir()]

    pdf = img2pdf.convert(imgs_paths)
    with open(output_path, "wb") as f:
        f.write(pdf)


def delete_temp_imgs(temp_dir):
    shutil.rmtree(temp_dir)


def check_valid_args(imgs_path, output_path):
    if output_path.exists():
        user_cont = "_"
        while (
            user_cont.lower().strip() != "y"
            and user_cont.lower().strip() != "n"
            and user_cont != ""
        ):
            user_cont = input(
                f"Proceeding will overwrite the following file: {str(output_path)}\nContinue (Y/n): "
            )
            if user_cont.lower().strip() == "n":
                print("Operation canceled.")
                exit(0)

    if not imgs_path.is_dir():
        raise ValueError(f"Invalid input images path: {str(imgs_path)}")

    if not imgs_path.exists():
        raise ValueError(f"Input path in argument does not exist: {str(imgs_path)}")

    # TODO properly detect if path is valid, not if an output file already exists
    # if not output_path.is_file():
    #     raise ValueError(f"Invalid output path: {str(output_path)}")


def main(argv):
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "imgs_path",
        help="directory containing the images to be converted to a pdf",
        type=Path,
    )
    argparser.add_argument(
        "-o",
        "--output_path",
        help="the path, including file name, of the output pdf",
        type=Path,
    )
    argparser.add_argument(
        "-b", "--brightness", help="the brightness of the pdf", type=int, default=0
    )
    argparser.add_argument(
        "-c", "--contrast", help="the contrast of the pdf", type=int, default=0
    )

    args = argparser.parse_args()

    imgs_path = args.imgs_path
    output_path = args.output_path
    brightness = args.brightness
    contrast = args.contrast

    if output_path is None:
        output_path = imgs_path / "combined_imgs.pdf"

    # imgs_path = Path(argv[0].replace('"', "").replace("'", ""))

    # if len(argv) > 1:
    #     output_path = Path(argv[1].replace('"', "").replace("'", ""))
    # else:
    #     output_path = imgs_path / "combined_imgs.pdf"

    check_valid_args(imgs_path, output_path)
    converted_dir = convert_imgs(imgs_path, brightness=brightness, contrast=contrast)
    try:
        imgs_to_pdf(converted_dir, get_output_path(output_path))
    finally:
        delete_temp_imgs(converted_dir)


if __name__ == "__main__":
    main(sys.argv)
#     # if len(sys.argv) < 2:
#     #     raise ValueError("Missing input images directory argument!")

#     # main(sys.argv[1:])
