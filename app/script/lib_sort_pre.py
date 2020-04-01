#!/share/public/software/Onc_Soft/python/3.6.8/bin/python3
# coding:utf-8
import os
import sys
import pandas as pd 
import csv 
bin=sys.path[0]
from pandas.core.frame import DataFrame
import random
import time
import copy
import shutil
try:
	input, outdir = sys.argv[1:]
except:
	print("Usage:\npython %s <input> <outdir> \n" % (sys.argv[0]))
	sys.exit(1)
#cd /share/work2/fuzhl4317/project/sort_lib && python lib_sort_auto/script/lib_sort_pre.py word/终文库排版模型整合_1.xlsx output_3
def setDir(filepath):
	'''
	如果文件夹不存在就创建，如果文件存在就清空！
	:param filepath:需要创建的文件夹路径
	:return:
	'''
	if not os.path.exists(filepath):
		os.mkdir(filepath)
	else:
		shutil.rmtree(filepath)
		time.sleep(1)
		os.mkdir(filepath)

def addtodict2(thedict, key_a, key_b, val): 
	if key_a in thedict:
		thedict[key_a].update({key_b: val})
	else:
		thedict.update({key_a:{key_b: val}})

def lib_per_format(lib_cycle,sample_cycle,project_primer,input,date):
	dict_kongwei_number=dict(zip([chr(x)+str(y)  for y in range(1,13) for x in range(65,73)],[i for i in range(1,97)]))
	with open (input, encoding='UTF-8') as i:
		lines=csv.reader(i,delimiter='\t')
		#print ("input:"+input)
		head=next(lines)
		h=['循环数','primer','group_type','max_num','shoukong','cv','glue_grade']
		head=h+head
		IDT=0
		for line in lines:
			da=[]
			project_type,sample,primer,cv,glue_grade,shoukong,kongwei=line[1],line[3],line[5],line[12],line[13],line[14],line[15]
			#循环数clo1
			cv=float(cv)
			cv=round(cv)
			#print (project_primer)
			if project_type in project_primer.keys():
				if project_primer[project_type]['primer'] == primer:
					pass
				else:
					print('警告：检测项目\"%s\"与引物版本\"%s\"不配对,应该为\"%s\":'%(project_type,primer,project_primer[project_type]['primer']))
			else:
				print ('陌生的检测项目\"%s\"' %project_type)

			if primer in lib_cycle.keys(): 
				da.extend([lib_cycle[primer]['cycle']])
			else:
				da.extend(['-'])
				print ("primer error:",primer)
			#引物版本 clo2
			da.append(primer)
			#样本类型（样本名倒数第二位字母） clo3 
			#最大杂交数统一为4
			group_type=sample[-2]
			#print ('group_type:',group_type,sample)
			if group_type in sample_cycle.keys():  
				da.extend([sample_cycle[group_type]['hyb_No.']])
			else:
				da.extend(['-'])
			#是否提供孔位号，提供了孔位号的，按孔位好分组，其余条件都不考虑,clo4
			if kongwei in dict_kongwei_number.keys():
				da.append(dict_kongwei_number[kongwei])
			else:
				da.append(0)

			#NC/PC,受控NCPC分开，受控非受控分开；受控PC=1 受控NC=2  受控=3  非受控NCPC=4,非受控
			#if sample.startswith('NC') or sample.startswith('PC'): #clo5
			if shoukong=='Y' and sample.startswith('PC'):
				da.append('1')
			elif shoukong=='Y' and sample.startswith('NC'):
				da.append('2')
			elif shoukong=='Y':
				da.append('3')
			elif sample.startswith('PC') and sample.startswith('NC'):
				da.append('4')
			else:
				da.append('5')

			#IDT非c开头clo5
			if  primer.startswith('IDT') and not(sample.startswith('C')): 
				IDT+=1
				da[4]=str(da[4])+str(IDT)
				print ("IDT非C开头样本%s编号%s:"%(sample,da[4]))
			if group_type == 'T' :
				if cv == 25 or cv == 50:
					#print ('cv:',cv)
					cv=1000 #赋值一个特别大的数，排序后就在最后了
				else: 
					cv=100
			da.extend([cv,glue_grade]) #clo6,7
			da.extend(line)
			date.append(da)
	#date.insert(0,head)
	df=DataFrame(date)
	#print (df)
	df_sort=df.sort_values(by=[3,0,1,2,4,5,6],ascending=[True,False,True,True,True,True,True])

	df_sort.to_csv(outdir+'/temp_sort.txt' , encoding = 'utf-8',sep = '\t',header = False,index=0 )

	uniq_raw=5*['0']
#	print (uniq_raw)
	group=0
	cv_min=0
	gg_min=0
	groupdf=[]
	groupdf_temp=[]
	C_uniq=[]
	name_uniq=[]
	primer=[]
	group_num=0  #组内计数
	group_C={}
	group_primer={}
	dict_kongwei_group={}
	kongwei=0
	name_pre='ON'+time.strftime("%y%m%d-",time.localtime(time.time()))
	#cycle_10=0
	head=['出库编号','barcode','cv_min_divide_max','glue_grade_diff']+head
	#print ("head:",head)
	colum=[13,14,15,16,18,17,1,5,24,25]
	g1=[head[i-1] for i in colum]
	#L1.insert(1, 'Baidu')
	g1.insert(6,'体积')
	g1.insert(6,'终文库Q值')
	g1.insert(6,'index')
	g1.insert(5,'500ng建库')
	groupdf.append(g1)
	for index,row in df_sort.iterrows():
		g=[]
		uniq_col_1_5=list(row[0:5])
		cv_min_divide_max=(int(float(cv_min))+1)/(int(float(row[5])+1))
		gg_diff=float(row[6])-float(gg_min)
		group_num+=1
		name=row[11].split('-')[0]
		cycle=row[0]
		if row[3]!=0 :
			#cycle=str(cycle)+str(row[3])
			if row[3]==kongwei :
				pass
			else:
				group_num=1
				group+=1
				uniq_raw=uniq_col_1_5
				cv_min=row[5]
				gg_min=row[6]
				C_uniq=[]
				name_uniq=[]
				primer=[]
		elif uniq_col_1_5!=uniq_raw or cv_min_divide_max<0.7 or gg_diff>30 or row[11] in C_uniq or group_num>4 or name in name_uniq:
			group_num=1
			group+=1
			uniq_raw=uniq_col_1_5
			cv_min=row[5]
			gg_min=row[6]
			primer=[]
			C_uniq=[]
			name_uniq=[]
		primer=row[1]
		cycle_C=str(row[0])+'_'+row[11]
		kongwei=row[3]

		#if row[3]=='1':
		# 	cycle=str(cycle)+'_NCPC'
		# elif row[4]=='2':
		# 	cycle=str(cycle)+'_NCPC'
		C_uniq.append(cycle_C)
		name_uniq.append(name)
		group_name=name_pre+str(group)
		if row[3]!=0 :
			addtodict2(dict_kongwei_group,cycle,kongwei-1,group_name)
			#dict_kongwei_group[cyc][kongwei-1]=group_name
		if group >96:
			print ("分组个数超过96个，请减少输入样本数")
			exit(1)
		addtodict2(group_C,cycle,group_name,C_uniq)
		group_primer[group_name]=primer
		cv_min_divide_max=float('%.2f' % cv_min_divide_max)
		g.extend([group_name,row[11],cv_min_divide_max,gg_diff])
		g.extend(list(row))
		#13	14	15	16	18	500ng建库	17	index	终文库Q值	19	1	5
		#1	C69	0.01	330.0	10	GP_v10_102	2	8	0	100	330	20200101	遗传性肿瘤57基因全外显子检测	白细胞	C2000736-W1WA	C69	GP_v10_102	74.3891	30	2231.673	7.7	12.987012987013	4.51298701298701	100	330	6
		
		g1=[g[i-1] for i in colum]
		g1.insert(6,'')
		g1.insert(6,'')
		g1.insert(6,'')
		ng500 = format(500/float(g[17]),'.2f')
		g1.insert(5,ng500)
		g_temp=g
		groupdf_temp.append(g_temp)
		
		groupdf.append(g1)
	sort_96_orifice_plate(group_C,groupdf,dict_kongwei_group,group_primer)
	groupdf_temp.insert(0,head)
	df_temp=DataFrame(groupdf_temp)
	#df=DataFrame(groupdf)
	df_temp.to_csv(outdir+'/temp_group.txt' , encoding = 'utf-8',sep = '\t',header = False,index=0 )
	#df.to_csv(outdir+'/建库详情.txt' , encoding = 'utf-8',sep = '\t',header = False,index=0 )
	#print ('dict_kongwei_group',dict_kongwei_group)

def sort_96_orifice_plate(group_C_raw,groupdf_out,dict_kongwei_group,group_primer):
	dict_group_num_96kongban_num=dict(zip([i for i in range(1,97)],[chr(x)+str(y)  for y in range(1,13) for x in range(65,73)]))

	front=[]
	left=[]
	output_list={}
	output_group_name={}
	output_cycle={}
	output_primer={}
	box_group={}
	uniq=[] #取并集	
	time=0
	box_ncpc=0
	#print('group_C_raw', group_C_raw)
	cyc='12_NCPC'
	if cyc in group_C_raw.keys():
		group_C=copy.deepcopy(group_C_raw)
		time+=1
		flag=0
		box_12_NCPC_num=len(group_C[cyc].keys())
		box=0
		for key,v in sorted(group_C[cyc].items()):
			#print (key)
			output_list[box]=group_C[cyc][key]
			output_group_name[box]=key
			box_group[key]=box
			output_cycle[box]=cyc
			del group_C[cyc][key]
			flag+=1
			box+=1
			#print(output_list)
		print ("cycle 12_NCPC run times:",time)	
		box_ncpc=box

	cyc=12
	box_12_num=0
	if cyc in group_C_raw.keys():
		for r in range(0,20,1):
			group_C=copy.deepcopy(group_C_raw)
			time+=1
			flag=0
			box_12_num=len(group_C[cyc].keys())
			for box in range(box_ncpc,(box_12_num+box_ncpc),1):
				if box>0:
					front=output_list[int(box)-1]
				if box>7:
					left=output_list[int(box)-8]
				uniq=list(set(left).union(set(front)))
				time_1=0
				while len(group_C[cyc].keys())!=0:
					#print ('len:',len(group_C[cyc].keys()))
					time_1+=1
					exit=0
					if time_1>2*box_12_num:
						exit=1
						#sys.exit(1)
						break
					#print list(set(a).intersection(set(b))) #取交集
					#print ('box',box)
					if 10 in dict_kongwei_group.keys() and box in dict_kongwei_group[10].keys():
						print ('退出:标记的孔位号{0}会导致循环数{1}无法连续排列,请修改孔位编号.\n'.format(dict_group_num_96kongban_num[box+1],cyc))
						sys.exit()
					if cyc in dict_kongwei_group.keys() and box in dict_kongwei_group[cyc].keys():
						#print ('指定孔位',dict_group_num_96kongban_num[box+1],box)
						key=dict_kongwei_group[cyc][box]
					else:
						key=random.choice(list(group_C[cyc].keys()))

					#print ('group_C,cyc,key',group_C[cyc][key],cyc,key,"uniq:",uniq)
					if key not in group_C[cyc].keys() :
						continue
					if list(set(group_C[cyc][key]).intersection(set(uniq))):
						#print ("next:",key,group_C[cyc][key])
						pass
					else:
						output_list[box]=group_C[cyc][key]
						output_primer[box]=group_primer[key]
						output_group_name[box]=key
						box_group[key]=box
						output_cycle[box]=cyc
						del group_C[cyc][key]
						flag+=1
						#print(output_list)
						break
				if exit==1:
					print ('random %s time' %(r))
					break
			if flag==box_12_num:
				#print ("flag,box, box_12_num:",flag,box ,box_12_num)
				break

	print ("cycle 12 run times:",time)	

	box12=box_12_num+box_ncpc
	cyc=10
	if cyc in group_C_raw.keys():
		for r in range(0,20,1):
			group_C=copy.deepcopy(group_C_raw)
			box_10_num=len(group_C_raw[10].keys())
			time+=1
			flag=0	
			for box in range(box12,(box_10_num+box12),1):
				if box>0:
					front=output_list[int(box)-1]
				if box>7:
					left=output_list[int(box)-8]
				uniq=list(set(left).union(set(front)))
				time_1=0
				while len(group_C[cyc].keys())!=0:
					time_1+=1
					exit=0
					if time_1>2*box_10_num:
						exit=1
						break

					if 12 in  dict_kongwei_group.keys() and box in dict_kongwei_group[12].keys():
						print ('退出:标记的孔位号{0}会导致循环数{1}无法连续排列,请修改孔位编号.\n'.format(dict_group_num_96kongban_num[box+1],cyc))
						sys.exit()
					if cyc in dict_kongwei_group.keys() and box in dict_kongwei_group[cyc].keys():
						key=dict_kongwei_group[cyc][box]
						#print ('指定孔位',dict_group_num_96kongban_num[box+1],box)
					else:
						key=random.choice(list(group_C[cyc].keys()))
						#print ('key',key,box)
					if key not in group_C[cyc].keys() :
						continue
					if list(set(group_C[cyc][key]).intersection(set(uniq))):
						pass
					else:
						output_list[box]=group_C[cyc][key]
						output_primer[box]=group_primer[key]
						output_group_name[box]=key
						box_group[key]=box
						output_cycle[box]=cyc
						#print ("delete:",key)
						del group_C[cyc][key]
						flag+=1
						#print(output_list)
						break
				if exit==1:
					print ('random %s time' %(r))
					break
			if flag==box_10_num:
				break
	print ("cycle 10 run times:",time)



	#print (groupdf_out)
	#name_pre='ON'+time.strftime("%y%m%d-",time.localtime(time.time()))
	head=groupdf_out[0]
	head.append("96孔板编号")
	#print ('head:',head)
	groupdf_out_96kongban=[]
	groupdf_out_96kongban.append(head)
	for line in groupdf_out[1:]:
		group_name=line[10]
		#print ('group_name',group_name)
		group_name_num=group_name.split('-')[1]
		#print ('group_name_split',group_name_num)
		if group_name in box_group.keys():
			o96_df_loc=dict_group_num_96kongban_num[box_group[group_name]+1]
			line.append(o96_df_loc)  #box_group[group_name] 96孔板数字位置
		else:
			sys.exit(1)

		groupdf_out_96kongban.append(line)
	#print (groupdf_out_96kongban)
	df=DataFrame(groupdf_out_96kongban)
	df.to_csv(outdir+'/建库详情.txt' , encoding = 'utf-8',sep = '\t',header = False,index=0 )

	outdict={'temp_check_cycle_barcode_df':output_list,'自动排版样本编号':output_group_name,'自动排版循环数':output_cycle,'自动排版引物版本':output_primer}
	for key,out_type in outdict.items():	
		colum=0
		#['第%s列'%i for i in  range(1,9)]
		groupdf=[]
		df_line=['第1列']
		name=key
		c=len(out_type.keys())%8
		index=1
		for value in out_type.values():
			colum+=1
			df_line.append(value)
			if colum==8:
				colum=0
				groupdf.append(df_line)
				index+=1
				index_num='第'+str(index)+'列'
				df_line=[index_num]
		if c!=0 and index >1 :
			groupdf.append(df_line)

		df=DataFrame(groupdf)
		df=df.T
		df.fillna(' ',inplace=True)
		#print (df)
		df.to_csv(outdir+'/'+name+'.txt' , encoding = 'utf-8',sep = '\t',header = False,index=0)

def main():
	print("当前时间"+time.strftime("%y:%m:%d",time.localtime(time.time())))

	df_config_lib=pd.read_csv(bin+'/config_lib_cycle.txt',sep='\t',index_col=0,header=0)
	lib_cycle=df_config_lib.to_dict(orient='index')
	#print (lib_cycle)
	df_config_sample=pd.read_csv(bin+'/config_sample_cycle.txt',sep='\t',index_col=0,header=0)
	sample_cycle=df_config_sample.to_dict(orient='index')
	df_config_project_primer=pd.read_csv(bin+'/config_check_project_primer.txt',sep='\t',index_col=0,header=0)
	project_primer=df_config_project_primer.to_dict(orient='index')

	#excel转txt，提取第一个sheet，约定sheet名为：Sheet1
	global input 
	global outdir
	if not os.path.exists(outdir):
		os.mkdir(outdir)
	folder_path, tempfile_name = os.path.split(input)
	file_name,extension=os.path.splitext(tempfile_name)
	print ('输入文件:',tempfile_name)
	if extension=='.xls' or extension=='.xlsx': #or file_name.endswith('xlsx'):
		#script/Transform_excel.py  Split -e input_file/终文库排版模型整合.xlsx -o  output_1/modeinput_v0/
		cmd='python '+bin+'/Transform_excel.py Split -e '+input+' -o '+outdir+'/'+file_name
		os.system(cmd)
		input=outdir+'/'+file_name+'/Sheet1.txt'
		#print ("input:",input)
	outdir=outdir+'/'+file_name+'_out'
	setDir(outdir)
	shutil.copy(input,outdir)

	date=[]
	df_sort=lib_per_format(lib_cycle,sample_cycle,project_primer,input,date)

	cmd='python '+bin+'/Transform_excel.py Merge -I '+outdir+' -O '+ outdir +'_result -P '+file_name+'_sort'
	os.system(cmd)
	print("运行完成")

if __name__ == "__main__":
	main()
'''
建库时间	检测项目	样本类型	样本编号	Barcode	引物版本	预文库Q	体积	总量	DNA浓度	建库（μL）	EB(μL)	预文库建库起始量	胶图级别	胶图级别	备注：
20200101	血液31检测	血浆	NCPV24006-P1PA	C40	SPS_v20_31	89.04	43	3828.72	6	5	36.5	30	180	1
20200101	胸水31检测	胸水全液	Z19R02148-X1XA	C06	SPS_v20_31	116.99	43	5030.57	1.24	41.5	0	51.46	210	2
'''
