from pydub import AudioSegment

def get_speechace_audio_list(audio_file, subtitles, indices_to_split, output_dir):

    # reduce audio file size
    audio = AudioSegment.from_file(audio_file).split_to_mono()[0].set_frame_rate(16000)

    # split audio into chunks
    start_chunk = 0
    audio_for_speechace = []
    index = 0
    for i in indices_to_split:
        start = 1000*subtitles[start_chunk].start.total_seconds()
        end = 1000*subtitles[i-1].end.total_seconds()
        audio_chunk = audio[start:end]

        audio_chunk.export(output_dir+"audio_chunk{0}.wav".format(index), format="wav")
        audio_for_speechace.append(output_dir+"audio_chunk{0}.wav".format(index))

        index += 1
        start_chunk = i

    return audio_for_speechace


