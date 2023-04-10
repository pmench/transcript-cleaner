import secrets
import openai
from nltk import word_tokenize
from tqdm import tqdm
import sys
from pathlib import Path

"""
This program is intended to be used for the correction of machine-generated
transcripts. It passes the text of the transcript to OpenAI's API and
returns text corrected by the selected OpenAI model.

https://platform.openai.com/docs/introduction
"""

openai.api_key = secrets.open_ai_key


def read_txt(filepath, encoding='utf-8', strip=True):
    """
    Given a filepath, this function reads a text file line by line,
    removing whitespace and trailing newline escape characters.

    Parameters:
        filepath (str): path to file.
        encoding (str): name of encoding for file.
        strip (bool): remove white space and new line characters if True.
    Returns:
        list: list of lines in file.
    """
    with open(filepath, 'r', encoding=encoding) as file_obj:
        if strip:
            data = [line.strip() for line in file_obj]
            return data
        else:
            return file_obj.readlines()


def write_txt(filepath, text, encoding='utf-8'):
    """"
    Given a filepath and a list of text, this function writes the text
    to a plain text file.

    Parameters:
        filepath (str): path for file.
        text (list): list containing text to write to file.
        encoding (str): encoding for text.
    Returns
        None
    """
    try:
        with open(filepath, 'w', encoding=encoding) as file_obj:
            file_obj.writelines(text)
            print('Success! Check your chosen directory for your text.')
    except Exception as e:
        print(f"Error writing file. {e}. Try again.")


def call_openai(model, prompt):
    """
    Calls the OpenAI API (https://platform.openai.com/docs/introduction)
    using the given model and prompt. Supported models are currently:
        - gpt-4
        - gpt-4-0314
        - gpt-4-32k
        - gpt-4-32k-0314
        - gpt-3.5-turbo
        - gpt-3.5-turbo-0301
    https://platform.openai.com/docs/models/model-endpoint-compatibility

    Parameters:
        model (str): OpenAI chat model to use for correction.
        prompt (str): text to pass to the model.
    Returns:
        string
    """
    try:
        return openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant'},
                {'role': 'user', 'content': prompt}
            ]
        )['choices'][0]['message']['content']
    except Exception as e:
        print(f"There was an error with the API: {e}.")


def process_txt(text, chunk_size=20, tkn_limit=800):
    """
    This function checks the number of tokens in the passed in text and if
    it exceeds the token limit, separates the text into chunks of 20 lines.

    Parameters:
        text (list): list of strings from text file.
        chunk_size (int): limit on the number of lines of text per chunk.
        tkn_limit (int): maximum number of tokens allowed before text is
            separated into chunks.
    Returns:
        list of lists, each containing text chunk.

    """
    tokens = []
    chunks = []
    chunk = []
    limit = chunk_size
    for element in text:
        tokens.extend(word_tokenize(element))
    if len(tokens) > tkn_limit:
        while len(text) > limit:
            for i in range(limit):
                chunk.append(text[i])
                if i == limit - 1:
                    chunks.append(chunk.copy())
                    chunk.clear()
                    for element in text[:i]:
                        text.remove(element)
        chunks.append(text)
    else:
        return text
    return chunks


def edit_text(text, mod='gpt-3.5-turbo'):
    """
    This function builds the corrected text of a transcript from the
    chunked version of the transcript, passing each chunk to the
    call_openai function for corrections.

    Parameters:
        text (list): list of lists containing text chunks.
        mod (str): string specifying the OpenAI model to use.
    Returns:
        list of strings
    """
    transcript = []
    for chunk in tqdm(text, 'Communicating with API'):
        txt = ''.join(chunk)
        model = mod
        prompt = 'Can you correct this transcript? Do not add words or remove timestamps: ' + txt
        response = call_openai(model, prompt)
        transcript.append(response)
    return transcript


def main():
    """
    Entry point for program.

    Parameters:
        None.
    Returns:
        None.
    """

    print(
        '############################\n'
        '********* Welcome *********\n'
        '############################'
    )
    print(
        "\nThis tool will help correct transcripts using OpenAI's language"
        " models. To start, you need:\n"
        "(1) your transcript in plain text format (.txt)\n"
        "(2) the filepath of the transcript you would like corrected.\n"
    )
    print(
        '!!!!!!!\n'
        'NOTE: The tool will make mistakes! Double-check the text before'
        ' using and NEVER upload any sensitive information.\n'
        '!!!!!!!\n'
    )

    while True:

        usr_request = input(
            '\nEnter the filepath of the text you would like corrected.\n'
            "Or type 'exit' to end the program.\n"
        )
        if usr_request == 'exit':
            sys.exit('Goodbye!')
        else:
            obj = Path(usr_request)
            if obj.exists():
                text = read_txt(usr_request)
                processed = process_txt(text)
                transcript = edit_text(processed, 'gpt-3.5-turbo')
                while True:
                    usr_output = input(
                        '\nWhere would you like to save the corrected text?\n'
                        'Enter the filepath for the text (including the file name).\n'
                    )
                    confirm = input(
                        f"\nYou entered:\n{usr_output}\nIs that accurate? [y / n]\n")
                    if usr_output == usr_request:
                        confirm = input(
                            f"\n!WARNING! The filepath for your corrected file"
                            f" is the same as your original file.\n"
                            f"\noriginal: {usr_request}\ncorrected: {usr_output}\n"
                            f"\nThis will overwrite your original file. Do"
                            f" you want to continue? [y / n]"
                        )
                    if confirm == 'y':
                        break
                write_txt(usr_output, transcript)
            else:
                print(f"Invalid filepath. {usr_request} does not exist.")


if __name__ == '__main__':
    main()
