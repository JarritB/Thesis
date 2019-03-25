# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 16:31:54 2018

@author: Jarrit
"""
import re

def printArray(A):
    for i in range(0,len(A),1):
        for j in range(0,len(A[i])):
            print(f'{str(A[i][j]):8}',end='')
        print()
    print()
        

def main():
    
    comments=""
    Values = []
    SymPos = []
    Atoms = []
    print("main functie")
    while(1):
        filename = input("Which file: ")
        try:
            file = open(filename,"r")
            break
        except:
            print ("File %s not found.."%(filename))
            continue
    cnaam = (file.readline())[5:].strip()
    print("Naam: "+cnaam+"\n")
    text = "#"
    while(text[0].strip() in ['#',''] ):
        comments += text
        text = (file.readline())
    print(comments)
    
    for n in range(0,6,1):    
        ite = re.finditer(r'(\d+)[.](\d+)',text)
        for i in ite: 
            Values.append(float(text[i.start():i.end()])) 
        text = file.readline()
    print(Values); 
    
    while(file.readline().strip() != "loop_"):
        pass
    file.readline()
    
    while(1):
        text = file.readline()
        T = text.strip("\'\n").split(',')
        if(T[0] == '' or T[0] == "loop_"):break
        SymPos.append(T)
        
    printArray(SymPos)
    
    while(file.readline().strip() != "loop_"):
        pass
    while(1):    
        text = file.readline()
        if(text == ""):
            break;
        if(text != '\n' and text[0] != "_"):
            Atoms.append(text.strip().split())              
    printArray(Atoms)
        
    
main()
