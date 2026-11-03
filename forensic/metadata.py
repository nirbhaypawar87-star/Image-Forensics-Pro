
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io


def _convert_gps_value(value):
    """Convert an EXIF GPS coordinate component to a float."""
    try:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            return float(value.numerator) / float(value.denominator)

        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _dms_to_decimal(dms, direction):
    """Convert GPS degrees, minutes and seconds to decimal coordinates."""
    try:
        degrees = _convert_gps_value(dms[0])
        minutes = _convert_gps_value(dms[1])
        seconds = _convert_gps_value(dms[2])

        if degrees is None or minutes is None or seconds is None:
            return None

        decimal = degrees + minutes / 60 + seconds / 3600

        if str(direction).upper() in ("S", "W"):
            decimal = -decimal

        return decimal
    except (IndexError, TypeError):
        return None


def extract_metadata(image_bytes):
    """Extract image properties and available EXIF metadata."""
    metadata = {}

    with Image.open(io.BytesIO(image_bytes)) as image:
        metadata["Format"] = image.format or "Unknown"
        metadata["Width"] = image.width
        metadata["Height"] = image.height
        metadata["Color Mode"] = image.mode
        metadata["File Size (bytes)"] = len(image_bytes)

        try:
            exif_data = image.getexif()

            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, str(tag_id))

                if tag_name == "GPSInfo":
                    continue

                try:
                    metadata[str(tag_name)] = str(value)
                except Exception:
                    metadata[str(tag_name)] = "Unreadable"

            # Extract nested GPS metadata when available.
            gps_info = {}

            try:
                gps_ifd = exif_data.get_ifd(0x8825)
                for tag_id, value in gps_ifd.items():
                    gps_name = GPSTAGS.get(tag_id, str(tag_id))
                    gps_info[gps_name] = value
            except (AttributeError, KeyError, TypeError, ValueError):
                pass

            if gps_info:
                for key, value in gps_info.items():
                    if key not in ("GPSLatitude", "GPSLatitudeRef",
                                   "GPSLongitude", "GPSLongitudeRef"):
                        metadata[f"GPS {key}"] = str(value)

                latitude = gps_info.get("GPSLatitude")
                latitude_ref = gps_info.get("GPSLatitudeRef")
                longitude = gps_info.get("GPSLongitude")
                longitude_ref = gps_info.get("GPSLongitudeRef")

                if latitude and latitude_ref and longitude and longitude_ref:
                    lat = _dms_to_decimal(latitude, latitude_ref)
                    lon = _dms_to_decimal(longitude, longitude_ref)

                    if lat is not None and lon is not None:
                        metadata["GPS Latitude"] = lat
                        metadata["GPS Longitude"] = lon

        except Exception as error:
            metadata["EXIF Read Status"] = f"Could not fully read EXIF: {error}"

        metadata.setdefault(
            "Date/Time Original",
            metadata.get("DateTimeOriginal", "Not available")
        )
        metadata.setdefault(
            "Camera Make",
            metadata.get("Make", "Not available")
        )
        metadata.setdefault(
            "Camera Model",
            metadata.get("Model", "Not available")
        )

        if "GPS Latitude" not in metadata:
            metadata["GPS Status"] = "GPS coordinates not available"

    return metadata
