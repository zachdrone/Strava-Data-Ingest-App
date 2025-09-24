from datetime import datetime, timedelta, timezone
from xml.etree.ElementTree import Element, SubElement, tostring

import gpxpy
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.utils.boto3_singleton import get_boto3_client


def create_gpx_from_streams(stream_data, start_date_utc):
    latlng = stream_data.get("latlng", {}).get("data", [])
    altitude = stream_data.get("altitude", {}).get("data", [])
    elapsed_time = stream_data.get("time", {}).get("data", [])
    distance = stream_data.get("distance", {}).get("data", [])
    cadence = stream_data.get("cadence", {}).get("data", [])
    heartrate = stream_data.get("heartrate", {}).get("data", [])

    # activity_start_time_utc = activity.get("start_date")

    start_datetime = datetime.strptime(start_date_utc, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )

    gpx = Element("gpx", version="1.1", creator="ZachApp")
    trk = SubElement(gpx, "trk")
    name = SubElement(trk, "name")
    name.text = "Downloaded Activity"
    trkseg = SubElement(trk, "trkseg")

    for i in range(len(latlng)):
        trkpt = SubElement(
            trkseg, "trkpt", lat=str(latlng[i][0]), lon=str(latlng[i][1])
        )
        if i < len(altitude):
            ele = SubElement(trkpt, "ele")
            ele.text = str(altitude[i])
        if i < len(elapsed_time):
            timestamp = (
                start_datetime + timedelta(seconds=elapsed_time[i])
            ).isoformat()
            time_elem = SubElement(trkpt, "time")
            time_elem.text = timestamp

        extensions = SubElement(trkpt, "extensions")
        if i < len(distance):
            distance_elem = SubElement(extensions, "distance")
            distance_elem.text = str(distance[i])
        if i < len(cadence):
            cadence_elem = SubElement(extensions, "cadence")
            cadence_elem.text = str(cadence[i])
        if i < len(heartrate):
            heartrate_elem = SubElement(extensions, "heartrate")
            heartrate_elem.text = str(heartrate[i])

    gpx_data = tostring(gpx, encoding="utf-8", method="xml")

    return gpx_data


def get_gpx_from_s3(bucket, key):
    s3 = get_boto3_client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    gpx_data = response["Body"].read()
    return gpx_data


def gpx_to_parquet(gpx_data, s3_bucket_name, s3_file_key):
    # Parse the GPX data using gpxpy
    gpx = gpxpy.parse(gpx_data)

    # Prepare structured data for DataFrame
    data = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                entry = {
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                    "altitude": point.elevation,
                    "timestamp": point.time.isoformat(),
                }
                if point.extensions:
                    for extension in point.extensions:
                        entry[extension.tag] = float(extension.text)
                data.append(entry)

    # Convert to Pandas DataFrame
    df = pd.DataFrame(data)

    # Convert DataFrame to Parquet
    table = pa.Table.from_pandas(df)

    # Empty Check
    if table.num_rows == 0:
        return

    # Convert to byte buffer (memory) instead of file
    parquet_buffer = pa.BufferOutputStream()
    pq.write_table(table, parquet_buffer)

    # Now we have the Parquet data in memory, ready to be uploaded to S3
    parquet_data = parquet_buffer.getvalue().to_pybytes()

    # Use boto3 to upload the Parquet data to S3
    s3_client = get_boto3_client("s3")
    resp = s3_client.put_object(
        Bucket=s3_bucket_name, Key=s3_file_key, Body=parquet_data
    )

    print(f"Parquet file successfully uploaded to s3://{s3_bucket_name}/{s3_file_key}")
    print(resp)
