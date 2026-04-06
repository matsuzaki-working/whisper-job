from datetime import datetime, timedelta, timezone
from google.cloud import storage
import whisper
import os
import io
import csv


def generate_filename():
    JST = timezone(timedelta(hours=9))
    base = (datetime.now(JST) - timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )

    hour = base.hour
    date_part = base

    if hour < 5:
        hour += 24
        date_part -= timedelta(days=1)

    return date_part.strftime("%Y%m%d") + f"{hour:02}0000"


def main():
    print("=== JOB START ===")

    bucket_name = "openai_whisper"
    file_name = generate_filename()
    print(f"Processing file: {file_name}")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"tmp/{os.path.basename(file_name)}.mp3")

    local_path = f"/tmp/{os.path.basename(file_name)}"
    print(f"Download to: {local_path}")

    try:
        blob.download_to_filename(local_path)
    except Exception as e:
        print(f"Download failed: {e}")
        return  # Jobは終了

    # Whisperモデルロード（ここに移動するのが安全）
    model = whisper.load_model("large-v3-turb")

    print("Start transcription...")
    result = model.transcribe(local_path)

    #text = result["text"]
    #print("Upload result...")
    #output_blob = bucket.blob(f"transcripts/{os.path.basename(file_name)}.txt")
    #output_blob.upload_from_string(text)

    print("Convert to CSV...")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["start", "end", "text"])
    for segment in result["segments"]:
        writer.writerow([segment["start"], segment["end"], segment["text"]])
    csv_data = output.getvalue()
    
    print("Upload result...")
    output_blob = bucket.blob(f"transcripts/{os.path.basename(file_name)}.csv")
    output_blob.upload_from_string(csv_data, content_type="text/csv")

    try:
        os.remove(local_path)
        print("Temp file removed")
    except Exception as e:
        print(f"Remove failed: {e}")

    print("=== JOB END ===")


if __name__ == "__main__":
    main()
