#!/share/public/software/Onc_Soft/python/3.6.8/bin/python3
import argparse
import os
import pandas as pd
import sys
import re
#reload(sys)
#sys.setdefaultencoding('utf8')

##################################################################sub function 
def Merge (args):
    if not os.path.exists(args.indir):
        print ("Please import input directory\n");
        sys.exit()
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    file_content=[]
    writer = pd.ExcelWriter(os.path.join(args.outdir, args.prefix + '.xlsx'))
    for root,dirs,files in os.walk(args.indir,topdown=False):
        for file in files:
            pathfile = os.path.join(root,file)
            filename = os.path.splitext(file)[0]
            filename.split('.txt')
            if filename.startswith('temp'):
                continue
            if not os.path.getsize(pathfile):
                print (type(file_content))
                file_content=pd.DataFrame(columns = [''])
            elif file.endswith('.txt'):
                file_content = pd.read_csv(pathfile,sep = "\t",header = None)
            elif file.endswith('.xls'):
                file_content = pd.read_excel(pathfile,sep = "\t",header = None)
            elif file.endswith('.xlsx'):
               file_content = pd.read_excel(pathfile,sep = "\t",header = None)

            file_content.to_excel(writer,filename,header = False,index=False)
            
    writer.save()



def Split (args):
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    sheet_list = pd.read_excel(args.excel,sheet_name = None, index_col = 0 ,
                               header = None)
    sep="\t"
    suffix=".txt"
    if args.type == 'csv':
        sep=","
        suffix=".csv"
    for num in sheet_list:
        sheet_list[num].to_csv(os.path.join(args.outdir, num+suffix), 
                               encoding = 'utf-8',sep = sep,header = False )


################################################################# parameter
Parser = argparse.ArgumentParser(description="File split and merge\n")
subparsers = Parser.add_subparsers(help = "Create sub command")

Parser_a = subparsers.add_parser('Merge',help = "Merge file")
Parser_a.add_argument("-I","--indir",help="input directory\n")
Parser_a.add_argument("-O","--outdir",help="output directory\n")
Parser_a.add_argument("-P","--prefix",help="output file prefix\n")
Parser_a.set_defaults(func = Merge)

Parser_s = subparsers.add_parser('Split',help = "Split file")
Parser_s.add_argument("-e","--excel",help="import excel file\n")
Parser_s.add_argument("-o","--outdir",help="output directory\n")
Parser_s.add_argument("-t","--type",help="output format,csv|table\n")
Parser_s.set_defaults(func = Split)

args = Parser.parse_args()
args.func(args)

