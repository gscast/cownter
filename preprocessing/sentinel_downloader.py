import os
import argparse
import sys
from typing import Any
from sentinelhub import SHConfig, BBox, CRS, DataCollection, SentinelHubRequest, \
    MimeType, DownloadRequest

class SentinelDownloader:
    def __init__(self, client_id: str, client_secret: str, instance_id: str) -> None:
        self.config = SHConfig
        self.config.sh_client_id = client_id
        self.config.sh_client_secret = client_secret
        self.config.instance_id = instance_id
    
    def __call__(self, coords, output_dir, img_name, resolution='10m') -> Any:

        bbox = BBox(coords, crs=CRS.WGS84)

        # Create a request for Sentinel-2 data
        request = SentinelHubRequest(
            data_folder=output_dir,
            evalscript="""
                //VERSION=3
                function setup() {
                    return {
                        input: ["B02", "B03", "B04"],
                        output: [
                            {
                                id: "default",
                                bands: 3,
                                sampleType: SampleType.AUTO
                            }
                        ]
                    };
                }

                function evaluatePixel(samples) {
                    return [samples.B04, samples.B03, samples.B02];
                }
            """,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time=("20220101", "20220131"),
                mosaicking_order="mostRecent",
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.PNG),
        ],
        bbox=bbox,
        size=(800, 800),
        config=self.config
    )

        # Execute the request
        request.save_data(redownload=True)

        # Rename the downloaded image
        image_path = os.path.join(output_dir, request.get_filename(img_name))
        os.rename(image_path, os.path.join(output_dir, f"{img_name}.png"))

def parse_args():
    parser = argparse.ArgumentParser(description="Download Sentinel-2 satellite image.")
    parser.add_argument("--file", type=float, required=True, help="File with coordinates")
    parser.add_argument("--output-folder", default="output", help="Output folder path")
    parser.add_argument("--image-name", default="sentinel_image", help="Image file name")

    return parser.parse_args(sys.argv[1:])

def read_coords(fp: str):
        coords = []
        with open(fp, 'r') as file:
            for line in file:
                # Split the line into two parts based on spaces and convert them to float
                parts = line.strip().split()
                if len(parts) == 2:
                    try:
                        pair = [float(parts[0]), float(parts[1])]
                        coords.append(pair)
                    except ValueError:
                        print(f"Skipping line: {line} - Not a valid pair of floats.")
        return coords

if __name__ == "__main__":
    downloader = SentinelDownloader(
        client_id="e4a8378d-3d6e-41a8-9f1b-5cc11a3556b0",
        client_secret="61M7AvZrMxmMtAzu7YF8a5Md8RTQoykwR1p4jciE",
        instance_id="a58f450c-bb04-4c96-90d5-7bf97148ba80"
    )

    args = parse_args()
    for coords in read_coords(args.file):
        fn = f"{args.image_name}_{coords[0]}_{coords[1]}"
        downloader(coords, args.output_folder, fn)
