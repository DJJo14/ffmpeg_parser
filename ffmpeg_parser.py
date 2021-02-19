import sys, subprocess, yaml, json
with open(r'/config/ffmpeg_parser.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
# print( config )
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
        print(f"arg {a} and next {arg[0]}", file=sys.stderr)
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



# ffprobe_cmd = ['ffprobe', '-v', 'quiet', '-show_streams', '-print_format', 'json', input_file]
# process = subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE)
# stdout = process.communicate()[0]
# input_file_codec = json.loads(stdout)
# if "streams" in input_file_codec:
#         #print(input_file_codec["streams"])
#         for s in input_file_codec["streams"]:
#                 #print(s )
#                 if "codec_name" in s:
#                         print( s["codec_name"])
#       if arg[a].startswith("-"):
#               print([arg[a], arg[a+1] ])

##==============================================================
## Build output arg
##================================================================
test_arguments = False
if test_arguments:
        output_list = []
        # output_list.append(config["ffmpeg_base"])
        output_list.append("./ffmpeg_parser.py")

        for k, i in decode_arg.items():
                if i == None:
                        output_list.append(k)
                else:
                        output_list.append(k)
                        output_list.append(i)

        output_list.append("-i")
        output_list.append(input_file)

        for k, i in encode_arg.items():
                if len(i) == 0:
                        output_list.append(k)
                else:
                        for o in i:
                                output_list.append(k)
                                output_list.append(o)

        print(output_list, file=sys.stderr)

        if sys.argv == output_list:
                print("itworks", file=sys.stderr)

        for i in range(len(sys.argv)):
                if sys.argv[i] == output_list[i]:
                        print(f"{sys.argv[i]} are eacual", file=sys.stderr)
                else:
                        print(f"{sys.argv[i]} != {output_list[i]}", file=sys.stderr)
else:
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


print(output_list, file=sys.stderr)



subprocess.run(output_list, cwd=config["ffmpeg_workdir"])