from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from mezzanine import template
from mezzanine.conf import settings
from mezzanine.core.templatetags import mezzanine_tags
from urllib import quote, unquote
import os
import StringIO
import logging

register = mezzanine_tags.register
logger = logging.getLogger(__name__)


@register.simple_tag
def thumbnail(image_url, width, height, upscale=True, quality=95, left=.5,
              top=.5, padding=False, padding_color="#fff"):
    """
    Given the URL to an image, resizes the image using the given width
    and height on the first time it is requested, and returns the URL
    to the new resized image. If width or height are zero then original
    ratio is maintained. When ``upscale`` is False, images smaller than
    the given size will not be grown to fill that size. The given width
    and height thus act as maximum dimensions.
    """

    if not image_url:
        return ""
    try:
        from PIL import Image, ImageFile, ImageOps
    except ImportError:
        logger.error("Cannot import PIL")
        import traceback
        traceback.print_exc()
        return ""

    image_url = unquote(str(image_url)).split("?")[0]
    if image_url.startswith(settings.MEDIA_URL):
        image_url = image_url.replace(settings.MEDIA_URL, "", 1)
    image_dir, image_name = os.path.split(image_url)
    image_prefix, image_ext = os.path.splitext(image_name)
    filetype = {".png": "PNG", ".gif": "GIF"}.get(image_ext, "JPEG")
    thumb_name = "%s-%sx%s" % (image_prefix, width, height)
    if not upscale:
        thumb_name += "-no-upscale"
    if left != .5 or top != .5:
        left = min(1, max(0, left))
        top = min(1, max(0, top))
        thumb_name = "%s-%sx%s" % (thumb_name, left, top)
    thumb_name += "-padded-%s" % padding_color if padding else ""
    thumb_name = "%s%s" % (thumb_name, image_ext)

    # `image_name` is used here for the directory path, as each image
    # requires its own sub-directory using its own name - this is so
    # we can consistently delete all thumbnails for an individual
    # image, which is something we do in filebrowser when a new image
    # is written, allowing us to purge any previously generated
    # thumbnails that may match a new image name.
    thumb_dir = os.path.join(settings.MEDIA_ROOT, image_dir,
                             settings.THUMBNAILS_DIR_NAME, image_name)

    thumb_path = os.path.join(thumb_dir, thumb_name)
    thumb_url = "%s/%s/%s" % (settings.THUMBNAILS_DIR_NAME,
                              quote(image_name.encode("utf-8")),
                              quote(thumb_name.encode("utf-8")))
    image_url_path = os.path.dirname(image_url)
    if image_url_path:
        thumb_url = "%s/%s" % (image_url_path, thumb_url)

    try:
        thumb_exists = default_storage.exists(thumb_path)
    except UnicodeEncodeError:
        # The image that was saved to a filesystem with utf-8 support,
        # but somehow the locale has changed and the filesystem does not
        # support utf-8.
        from mezzanine.core.exceptions import FileSystemEncodingChanged
        raise FileSystemEncodingChanged()
    if thumb_exists:
        # Thumbnail exists, don't generate it.
        return default_storage.url(thumb_url)
    elif not default_storage.exists(image_url):
        # Requested image does not exist, just return its URL.
        return default_storage.url(image_url)


    logger.info("Creating thumbnail for %s", image_url)

    f = default_storage.open(image_url)
    try:
        image = Image.open(f)
    except:
        # Invalid image format.
        return default_storage.url(image_url)

    image_info = image.info

    # Transpose to align the image to its orientation if necessary.
    # If the image is transposed, delete the exif information as
    # not all browsers support the CSS image-orientation:
    # - http://caniuse.com/#feat=css-image-orientation
    try:
        orientation = image._getexif().get(0x0112)
    except:
        orientation = None
    if orientation:
        methods = {
           2: (Image.FLIP_LEFT_RIGHT,),
           3: (Image.ROTATE_180,),
           4: (Image.FLIP_TOP_BOTTOM,),
           5: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_90),
           6: (Image.ROTATE_270,),
           7: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_270),
           8: (Image.ROTATE_90,)}.get(orientation, ())
        if methods:
            image_info.pop('exif', None)
            for method in methods:
                image = image.transpose(method)

    to_width = int(width)
    to_height = int(height)
    from_width = image.size[0]
    from_height = image.size[1]

    if not upscale:
        to_width = min(to_width, from_width)
        to_height = min(to_height, from_height)

    # Set dimensions.
    if to_width == 0:
        to_width = from_width * to_height // from_height
    elif to_height == 0:
        to_height = from_height * to_width // from_width
    if image.mode not in ("P", "L", "RGBA") and filetype not in ('JPG', 'JPEG'):
        try:
            image = image.convert("RGBA")
        except:
            return image_url
    # Required for progressive jpgs.
    ImageFile.MAXBLOCK = 2 * (max(image.size) ** 2)

    # Padding.
    if padding and to_width and to_height:
        from_ratio = float(from_width) / from_height
        to_ratio = float(to_width) / to_height
        pad_size = None
        if to_ratio < from_ratio:
            pad_height = int(to_height * (float(from_width) / to_width))
            pad_size = (from_width, pad_height)
            pad_top = (pad_height - from_height) // 2
            pad_left = 0
        elif to_ratio > from_ratio:
            pad_width = int(to_width * (float(from_height) / to_height))
            pad_size = (pad_width, from_height)
            pad_top = 0
            pad_left = (pad_width - from_width) // 2
        if pad_size is not None:
            pad_container = Image.new("RGBA", pad_size, padding_color)
            pad_container.paste(image, (pad_left, pad_top))
            image = pad_container

    # Create the thumbnail.
    to_size = (to_width, to_height)
    to_pos = (left, top)
    try:
        image = ImageOps.fit(image, to_size, Image.ANTIALIAS, 0, to_pos)
        data = StringIO.StringIO()
        image = image.save(data, filetype, quality=quality, **image_info)
        default_storage.save(unquote(thumb_url), ContentFile(data.getvalue()))
    except Exception:
        import traceback
        traceback.print_exc()
        return default_storage.url(image_url)
    return default_storage.url(thumb_url)
