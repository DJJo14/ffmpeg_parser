import sys, subprocess, yaml, json, os.path
if os.path.isfile(r'ffmpeg_parser.yaml'):
        config_file = r'ffmpeg_parser.yaml'
else:
        config_file = r'/config/ffmpeg_parser.yaml'
        
with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
# print( config )

print( ("h264" in config["codec_decoder"]) )
print( config["codec_decoder"]["h264"] )

arg = []

for a in sys.argv:
        arg.append(a)


decode_arg = {}
encode_arg = {}
preinput = False
input_file = None

print(f"I was called from {arg.pop(0)}", file=sys.stderr)
while len(arg) > 1:
        a = arg.pop(0)
        # print(f"arg {a} and next {arg[0]}", file=sys.stderr)
        if a == "-i":
                preinput = True
                input_file = arg.pop(0)
        elif a.startswith("-"):
                if preinput:
                        if arg[0].startswith("-") and (len(arg[0]) > 1 and not arg[0][1].isdigit() ):
                                encode_arg[ a ] = []
                        elif a in encode_arg:
                                encode_arg[ a ].append(arg.pop(0))
                        else:
                                encode_arg[ a ] = [arg.pop(0)]
                                
                else:
                        if arg[0].startswith("-") and (len(arg[0]) > 1 and not arg[0][1].isdigit() ):
                                decode_arg[ a ] = []
                        elif a in encode_arg:
                                encode_arg[ a ].append(arg.pop(0))
                        else:
                                decode_arg[ a ] = [arg.pop(0)]
                                 
        # if arg[a] == "-c" or arg[a][:len("-codec")] == "-codec":
        #         print(f"found codec { arg[a+1]} preinput:{preinput}")
        #         print(f"switch from input to output")
##==============================================================
## Check decoder codec
##==============================================================
input_video_decoder = None
input_video_decoder_arg = None

if "-codec:v:0" in decode_arg:
        input_video_decoder = decode_arg["-codec:v:0"][0]
        input_video_decoder_arg = "-codec:v:0"
elif "-codec:v" in decode_arg:
        input_video_decoder = decode_arg["-codec:v"][0]
        input_video_decoder_arg = "-codec:v"

##==============================================================
## Check input codec
##==============================================================
if input_video_decoder == None:
        print("No decoder found, locking up video codec", file=sys.stderr)
        ffprobe_cmd = [config["ffmpeg_ffprobe"], '-v', 'quiet', '-show_streams', '-print_format', 'json', input_file]
        process = subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE , cwd=config["ffmpeg_workdir"])
        stdout = process.communicate()[0]
        input_file_codec = json.loads(stdout)
        if "streams" in input_file_codec:
                #print(input_file_codec["streams"])
                for s in input_file_codec["streams"]:
                        #print(s)
                        if s["codec_type"] == "video" and "codec_name" in s:
                                print( f"found input codec: {s['codec_name']}")
                                input_video_decoder = s["codec_name"]
                                break
                else:
                        print("Could not note find input codec", file=sys.stderr)


##==============================================================
## Replace decoder
##==============================================================
if not (input_video_decoder == None and input_video_decoder_arg == None):
        if input_video_decoder_arg == None:
                input_video_decoder_arg = "-codec:v"
        
        if input_video_decoder in config["codec_decoder"]:
                old_decoder = input_video_decoder
                input_video_decoder = config["codec_decoder"][old_decoder]["replace"]
                print(f"replaceing decoder {old_decoder} with {input_video_decoder}")

                decode_arg[input_video_decoder_arg] = [input_video_decoder]

                for i in config["codec_decoder"][old_decoder]["add"].keys():
                        if i in decode_arg:
                                decode_arg[i].append(config["codec_decoder"][old_decoder]["add"][i])
                        else:
                                decode_arg[i] = [ config["codec_decoder"][old_decoder]["add"][i] ]
                
                for i in config["codec_decoder"][old_decoder]["remove"]:
                        if i in decode_arg:
                                del decode_arg[i]

                for i in config["codec_decoder"][old_decoder]["remove_encoder"]:
                        if i in encode_arg:
                                del encode_arg[i]
                                
                if len( config["codec_decoder"][old_decoder]["add_start"] ) >= 1:
                        decode_arg = {**config["codec_decoder"][old_decoder]["add_start"], **decode_arg}

##==============================================================
## Check encoder codec
##==============================================================
input_video_encoder = None
input_video_encoder_arg = None

if "-codec:v:0" in encode_arg:
        input_video_encoder = encode_arg["-codec:v:0"][0]
        input_video_encoder_arg = "-codec:v:0"
elif "-codec:v" in encode_arg:
        input_video_encoder = encode_arg["-codec:v"][0]
        input_video_encoder_arg = "-codec:v"

##==============================================================
## Replace encoder
##==============================================================
if not (input_video_encoder == None and input_video_encoder_arg == None):
        if input_video_encoder_arg == None:
                input_video_encoder = "-codec:v"
                
        
        if input_video_encoder in config["codec_encoder"]:
                old_encoder = input_video_encoder
                input_video_encoder = config["codec_encoder"][old_encoder]["replace"]
                print(f"replaceing decoder {old_encoder} with {input_video_encoder}", file=sys.stderr)

                encode_arg[input_video_encoder_arg] = [input_video_encoder]
                #split arguments in two, to add keys inbetween
                index_encoder = list(encode_arg.keys()).index(input_video_encoder_arg) + 1
                encode_arg_firsthalf = dict( list(encode_arg.items())[:index_encoder] )
                encode_arg_secondhalf = dict( list(encode_arg.items())[index_encoder:] )

                for i in config["codec_encoder"][old_encoder]["add"].keys():
                        if i in encode_arg_firsthalf:
                                encode_arg_firsthalf[i].append(config["codec_encoder"][old_encoder]["add"][i])
                        else:
                                encode_arg_firsthalf[i] = [ config["codec_encoder"][old_encoder]["add"][i] ]

                encode_arg = {**encode_arg_firsthalf, **encode_arg_secondhalf}
                

                for i in config["codec_encoder"][old_encoder]["remove"]:
                        if i in encode_arg:
                                del encode_arg[i]
                                
                if len( config["codec_encoder"][old_encoder]["add_start"] ) >= 1:
                        encode_arg = {**config["codec_encoder"][old_encoder]["add_start"], **encode_arg}

##==============================================================
## Build output arg
##================================================================

output_list = []
output_list.append(config["ffmpeg_base"])

for k, i in decode_arg.items():
        if len(i) == 0:
                output_list.append(str( k ) )
        else:
                for o in i:
                        output_list.append(str( k ) )
                        output_list.append(str( o ) )

output_list.append("-i")
output_list.append(input_file)

for k, i in encode_arg.items():
        if len(i) == 0:
                output_list.append(str( k ) )
        else:
                for o in i:
                        output_list.append(str( k ) )
                        output_list.append(str( o ) )

print(output_list, file=sys.stderr)


subprocess.run(output_list, cwd=config["ffmpeg_workdir"])