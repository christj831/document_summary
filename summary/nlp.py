from transformers import pipeline, AutoTokenizer
from nltk.tokenize import sent_tokenize

# Initialize summarization pipeline and tokenizer
model_name = "facebook/bart-large-cnn"
summarizer = pipeline("summarization", model=model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def split_text_into_chunks_safe(text, max_tokens=900):
    """
    Split the input text into chunks that are safe for the summarization model.
    Each chunk will not exceed the specified max_tokens after decoding.
    """
    tokens = tokenizer.encode(text, truncation=False)  # Encode the text into tokens without truncation
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]

        # Decode and validate the token count
        decoded_chunk = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        decoded_token_count = len(tokenizer.encode(decoded_chunk))

        # If the decoded chunk exceeds the limit, reduce its size
        while decoded_token_count > max_tokens and end > start:
            end -= 1
            chunk_tokens = tokens[start:end]
            decoded_chunk = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            decoded_token_count = len(tokenizer.encode(decoded_chunk))

        # Append valid chunk or handle errors
        if decoded_token_count <= max_tokens:
            chunks.append(decoded_chunk)
            start = end
        else:
            # Failsafe: Skip the problematic segment if it cannot fit
            print(f"Warning: Could not split chunk starting at token {start}. Skipping.")
            start = end

    return chunks


def summarize_text(text, num_sentences=5, max_tokens=900):
    """
    Summarize the input text into the desired number of sentences.
    """
    try:
        # Split the text into manageable chunks
        chunks = split_text_into_chunks_safe(text, max_tokens=max_tokens)

        # Summarize each chunk
        summaries = []
        for chunk in chunks:
            # Dynamically set max_length and min_length
            max_summary_length = num_sentences * 50  # Adjust for sentence length
            min_summary_length = max(num_sentences * 25, 10)  # Ensure a minimum length

            # Summarize the chunk
            summary = summarizer(
                chunk,
                max_length=max_summary_length,
                min_length=min_summary_length,
                do_sample=False
            )[0]['summary_text']
            summaries.append(summary)

        # Combine all chunk summaries into a single summary
        full_summary = " ".join(summaries)

        # Break the summary into sentences
        sentences = sent_tokenize(full_summary)

        # Retry if fewer sentences than requested
        while len(sentences) < num_sentences:
            print("Retrying with relaxed constraints...")
            combined_text = " ".join(chunks)
            retry_summary = summarizer(
                combined_text,
                max_length=(num_sentences + 2) * 50,  # Allow more tokens
                min_length=(num_sentences + 2) * 25,
                do_sample=False
            )[0]['summary_text']
            sentences = sent_tokenize(retry_summary)
            
            # Break loop if retry doesn't improve
            if len(sentences) <= len(sent_tokenize(full_summary)):
                break

        # Return the exact number of sentences, or all available if less
        if len(sentences) < num_sentences:
            print(f"Warning: Unable to generate {num_sentences} sentences. Returning {len(sentences)} sentences.")
            return " ".join(sentences)

        return " ".join(sentences[:num_sentences])

    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "An error occurred during summarization."
