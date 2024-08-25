import argparse, os, sys, select
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

import openai

from tqdm import tqdm
from pypdf import PdfReader

# Get the OpenAI API Key
if os.environ["OPENAI_API_KEY"]:

    API_key = os.environ["OPENAI_API_KEY"]

    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", required=True, type=str, help="Provide the path to the PDF")
    parser.add_argument('-a', "--audio", required=True, type=str, help="Provide the path to save your audio file.")

    # Optional args
    # 'nargs' param set to "2" forces the range flag to take 2 args
    parser.add_argument('-r', "--range", nargs=2, help="Specify a range of pages you wish to convert to audio. Ex: -r 76 152 (Narrate pages 76 to 152)")
    parser.add_argument('-v', "--voice", nargs=1, default="nova", choices=['nova', 'shimmer', 'onyx', 'fable', 'echo', 'alloy'], type=str, help="Specify the voice. Choices: 'nova', 'shimmer', 'onyx', 'fable', 'echo', 'alloy'")
    parser.add_argument('-m',"--model", nargs=1, default="tts-1", choices=['tts-1', 'tts-1-hd'], type=str, help="Specify the model. Choices: 'tts-1', 'tts-1-hd'")

    args = parser.parse_args()

    if bool(args.doc.endswith(".pdf")):

        # Get vars
        pdf_fullpath = args.doc
        pdf_range = args.range
        audio_fullpath = args.audio
        model = args.model
        voice = args.voice

        pages = ""
        if pdf_range:
            pages = f"{pdf_range[0]} to {pdf_range[1]}"
        else:
            pages = "all"

        print(f"""
            Model: {model},
            Audio: {audio_fullpath},
            PDF:   {pdf_fullpath},
            Pages: {pages}
                """)

        # Ensure the provided pdf_fullpath exists
        if os.path.exists(pdf_fullpath):

            # Get the pdf_fullpath to the PDF
            if os.access(pdf_fullpath, os.R_OK):
                reader = PdfReader(pdf_fullpath)

                # Create a string of the PDF
                pdf_str = ""

                # Load entire PDF into dictionary sort into {page: text}
                print("Extracting PDF page main text...")
                pdf_dict = {}
                total_pages = len(reader.pages)
                count = 0
                for pageobj in tqdm(reader.pages):
                    count += 1
                    info = {count: pageobj.extract_text()}
                    pdf_dict.update(info)

                # Handle the range_num arg here
                range_dict = {}

                if pdf_range and int(pdf_range[0]) <= int(pdf_range[1]):
                    for page_num, page_text in pdf_dict.items():
                        if page_num in range(int(pdf_range[0]), int(pdf_range[1]) + 1): # Add pages in the specified range to range_dict
                            range_dict[page_num] = page_text

                # Iterate through either range_dict or pdf_dict and append the contents to pdf_str
                if bool(range_dict):
                    for page_num, page_text in range_dict.items():
                        pdf_str += page_text
                else:
                    for page_num, page_text in pdf_dict.items():
                        pdf_str += page_text

                """
                - Break up the file into smaller chunks before sending to OpenAI 
                - Sample error', \'ctx\': {\'max_length\': 4096}}]', 'type': 'invalid_request_error', 'param': None, 'code': None}}
                - Assuming the sample error is referring to 4096 chars per request limit to the server
                - Need to chop up TTS API Request among separate smaller chunks, get the audio file back,
                then stitch them together into one big file...
                - According to OpenAI's TTS pricing scheme it costs $15 / 1M chars (not tokens) to use tts-1
                    $30 / 1M chars for tts-1-hd model
                    - Max number of tokens per request is 4096

                __________________________________________________________
                - Create a list of tasks for workers to work on
                - Tasklist will be a list of tuples
                    - [(unique_audio_fullpath, model, voice, unique_input), (unique_audio_fullpath, model, voice, unique_input), (etc)]
                """

                # Below is a list of inputs required for the input paramter required by the OpenAI sample request

                tasklist = []
                total_chars = len(pdf_str)
                input_list = []

                for chunk in range(0, total_chars, 4072):
                    input_chunks = pdf_str[chunk:chunk + 4072]
                    input_list.append(input_chunks)

                # Populate the tasklist
                audio_id = 0
                for input_chunk in input_list:
                    audio_id += 1
                    task = (f"part-{audio_id}-{audio_fullpath}", model, voice, input_chunk)
                    tasklist.append(task)

                """
                - A worker will send out a request
                - Below is a sample request
                ______________________________
                speech_file_path = Path(__file__).parent / "speech.mp3"
                    response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input="Today is a wonderful day to build something people love!"
                    )
                response.stream_to_file(speech_file_path)
                """

                # The tasklist has been assembled. It's time to spin up some workers and assign some tasks...
                def download(req_audio_fullpath, req_model, req_voice, req_input_chunk):
                    client = openai.OpenAI()

                    print(f"working on task: {req_audio_fullpath}")
                    
                    response = client.audio.speech.create(model=req_model, voice=req_voice, input=req_input_chunk)
                    
                    # At this time .stream_to_file() is deprecated.
                    # However OpenAI still uses this in their documentation...
                    response.stream_to_file(req_audio_fullpath) 
                    
                # max_workers can be changed to suit your needs
                with ThreadPoolExecutor(max_workers=8) as executor:

                    # Create a list to hold futures
                    futures = []
                    for task in tasklist:
                        audio_fullpath, model, voice, input_chunk = task # Tuple unpacking...
                        futures.append(executor.submit(download, audio_fullpath, model, voice, input_chunk))

                    # Handle the results as they complete
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            result = future.result()  # This will raise an exception if the download failed
                        except Exception as e:
                            print(f"Error occurred: {e}")
                
        else:
            print("Please ensure this program runs in a dir with read permissions and try again...")
            sys.exit()

    elif args.doc.endswith(".txt"):

        # Get vars
        txt_fullpath = args.doc
        audio_fullpath = args.audio
        model = args.model
        voice = args.voice

        print(f"""
            Model: {model},
            Audio: {audio_fullpath},
            TXT:   {txt_fullpath},
                """)

        # Ensure the provided txt_fullpath exists
        if os.path.exists(txt_fullpath):

            # Get the txt_fullpath to the txt
            if os.access(txt_fullpath, os.R_OK):

                # Create a string of the TXT
                txt_str = ""

                # Load entire txt into txt_str
                with open(txt_fullpath, "r") as f:
                    txt_str += f.read()

                tasklist = []
                total_chars = len(txt_str)
                input_list = []

                for chunk in range(0, total_chars, 4072):
                    input_chunks = txt_str[chunk:chunk + 4072]
                    input_list.append(input_chunks)

                audio_id = 0
                for input_chunk in input_list:
                    audio_id += 1
                    task = (f"part-{audio_id}-{audio_fullpath}", model, voice, input_chunk)
                    tasklist.append(task)

                def download(req_audio_fullpath, req_model, req_voice, req_input_chunk):
                    client = openai.OpenAI()

                    print(f"working on task: {req_audio_fullpath}")
                    
                    response = client.audio.speech.create(model=req_model, voice=req_voice, input=req_input_chunk)
                    
                    # At this time .stream_to_file() is deprecated.
                    # However OpenAI still uses this in their documentation...
                    response.stream_to_file(req_audio_fullpath) 
                    
                # max_workers can be changed to suit your needs
                with ThreadPoolExecutor(max_workers=8) as executor:

                    # Create a list to hold futures
                    futures = []
                    for task in tasklist:
                        audio_fullpath, model, voice, input_chunk = task # Tuple unpacking...
                        futures.append(executor.submit(download, audio_fullpath, model, voice, input_chunk))

                    # Handle the results as they complete
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            result = future.result()  # This will raise an exception if the download failed
                        except Exception as e:
                            print(f"Error occurred: {e}")                

    else:
        print("Please check your pdf_fullpath and try again")
        sys.exit()

else:
    print("Please add your $OPENAI_API_KEY to your env vars and try again...")
    sys.exit()
