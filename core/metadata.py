import piexif
import io
from datetime import datetime
import random
from PIL import Image
import os

def deg_to_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m/60) * 3600 * 100
    return ((d, 1), (m, 1), (int(s), 100))

def get_gps_exif(lat, lon):
    lat_ref = 'N' if lat >= 0 else 'S'
    lon_ref = 'E' if lon >= 0 else 'W'
    return {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref,
        piexif.GPSIFD.GPSLatitude: deg_to_dms(abs(lat)),
        piexif.GPSIFD.GPSLongitudeRef: lon_ref,
        piexif.GPSIFD.GPSLongitude: deg_to_dms(abs(lon))
    }

def create_xmp_credit(credit_text):
    """Generates raw XMP packet with Credit field."""
    xmp = f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 4.4.0">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
    xmlns:iptc="http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/">
   <photoshop:Credit>{credit_text}</photoshop:Credit>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""
    return xmp.encode('utf-8')

def process_metadata(image_bytes, profile, extra_params={}):
    """Example metadata injection for various profiles."""
    try:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        if profile == "iPhone 15 Pro":
            exif_dict["0th"][piexif.ImageIFD.Make] = "Apple"
            exif_dict["0th"][piexif.ImageIFD.Model] = "iPhone 15 Pro"
            exif_dict["0th"][piexif.ImageIFD.Software] = "17.1.2"
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            if "lat" in extra_params and "lon" in extra_params:
                exif_dict["GPS"] = get_gps_exif(extra_params["lat"], extra_params["lon"])
                
        elif profile == "Sony A7III":
            exif_dict["0th"][piexif.ImageIFD.Make] = "Sony"
            exif_dict["0th"][piexif.ImageIFD.Model] = "ILCE-7M3"
            exif_dict["0th"][piexif.ImageIFD.Software] = "ILCE-7M3 v4.01"
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            if "lat" in extra_params and "lon" in extra_params:
                exif_dict["GPS"] = get_gps_exif(extra_params["lat"], extra_params["lon"])

        elif profile == "Google Tag":
            exif_dict["0th"][piexif.ImageIFD.Software] = "Picasa"
            exif_dict["0th"][piexif.ImageIFD.Make] = "Google"
            exif_dict["0th"][piexif.ImageIFD.Model] = "Google Generative AI"
            desc = "Digital Source Type: http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = desc
            exif_dict["0th"][700] = create_xmp_credit("Made with Google AI")
            
        elif profile == "ChatGPT Tag":
            exif_dict["0th"][piexif.ImageIFD.Software] = "GPT-4o, OpenAI API"
            exif_dict["0th"][piexif.ImageIFD.Make] = "OpenAI"
            exif_dict["0th"][piexif.ImageIFD.Model] = "DALL-E 3"
            manifest_text = "JUMD Label: c2pa | Actions: c2pa.created | Digtial Source Type: trainedAlgorithmicMedia"
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = manifest_text.encode('utf-8')
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = "AI Generated Image"
            
        elif profile == "Midjourney Tag":
            prompt = extra_params.get("prompt", "A cat in space...")
            job_id = f"{random.randint(10000000, 99999999)}"
            desc = f"{prompt} --v 7 Job ID: {job_id}"
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = desc
            exif_dict["0th"][piexif.ImageIFD.Software] = "Midjourney v7"
            exif_dict["0th"][piexif.ImageIFD.Model] = "XMP Core 4.4.0-Exiv2" 
            
        exif_dict["Exif"][piexif.ExifIFD.ExifVersion] = b"0220"
        exif_bytes = piexif.dump(exif_dict)
        
        img = Image.open(io.BytesIO(image_bytes))
        out = io.BytesIO()
        img.save(out, format="JPEG", exif=exif_bytes, quality=95)
        return out.getvalue()
        
    except Exception as e:
        print(f"Error: {e}")
        return image_bytes

from PIL.ExifTags import TAGS

def extract_exif(image_source):
    """Extracts all available Metadata (EXIF + PNG Info + XMP) for display."""
    data = {}
    try:
        if isinstance(image_source, str):
            img = Image.open(image_source)
        else:
            image_source.seek(0)
            img = Image.open(image_source)
        
        exif = img.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                # Clean value
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', 'ignore').strip("\x00")
                    except:
                        value = f"<Binary {len(value)} bytes>"
                        
                data[str(tag_name)] = value

        for key, value in img.info.items():
            if key in ["exif", "xml", "photoshop", "icc_profile"]: 
                continue
            
            if isinstance(value, (str, int, float)):
                data[key] = value
            elif isinstance(value, bytes):
                try:
                    data[key] = value.decode('utf-8', 'ignore')
                except:
                    pass

        if not data:
            return {"Status": "No Metadata Class detected."}
            
        return data
        
    except Exception as e:
        return {"Status": f"Scan Error: {str(e)}"}
