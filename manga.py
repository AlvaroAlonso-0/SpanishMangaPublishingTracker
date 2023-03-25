import requests
import sys
import re
import os
from bs4 import BeautifulSoup

ENTER_ID = " * Enter the ID of the manga: "
HTML_PARSER = 'html.parser'
ID_LIST = 'id_list.txt'

def manga(id):
    url = f"https://www.listadomanga.es/coleccion.php?id={id}"
    response = requests.get(url)

    # Analizar el contenido HTML de la respuesta
    body = BeautifulSoup(response.content, HTML_PARSER).body
    header = body.find_all('h2')[0]
    volumes = body.find('table', {'style': 'padding: 0px; margin: 0px; border: 0px;'})
    tomos = volumes.find_all('table', {'class': 'ventana_id1'})

    # Redirigir salida a un archivo
    sys.stdout = open('tomos.txt', 'w')

    print(header.text)

    # Imprimir cada uno de los tomos
    for tomo in tomos:
        data = []
        
        # find the td element
        td = tomo.find('td',{'class':'cen'})

        data.append(td.find('img')['src'])
        data.append(td.find('br').previous_sibling.strip())
                
        for br in td.find_all('br'):
            if br.find_next_sibling().name == 'br':
                data.append(br.next_sibling.strip())
            else:
                data.append(td.find('a').text.strip())        

        # print the extracted information
        print('------------------')
        print(f"Image source: {data[0]}")
        print(f"Title: {data[1]}")
        print(f"Pages: {data[2]}")
        print(f"Price: {data[3]}")
        print(f"Date: {data[4]}")
        
    # Cerrar el archivo
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    
    return header.text.strip()
  
def novedades(mes,ano):
    url = f"https://www.listadomanga.es/calendario.php?mes={mes}&ano={ano}"
    response = requests.get(url)
    
    # Analizar el contenido HTML de la respuesta
    body = BeautifulSoup(response.content, HTML_PARSER).body
    links = body.find_all('a', href=re.compile(r'coleccion\.php\?id=\d+'))
    
    clean_links = []
    
    for link in links:
        if link.text.strip() != '':
            clean_links.append(link)
            
    with open(ID_LIST, 'r') as f:
        ids = {int(line.strip()) for line in f}
    
    f = open('novedades.txt', 'w')
    
    for link in clean_links:
        # If the id is exactly any number contained in one line of id_list.txt print it
        if int(link['href'].split('=')[1]) in ids:
            print(f'\t{link.text.strip()}')
            print(link.text.strip(), file=f)
            
    f.close()
      
def search(name):
    url = "https://www.listadomanga.es/lista.php"
    response = requests.get(url)
    
    # Analizar el contenido HTML de la respuesta
    body = BeautifulSoup(response.content, HTML_PARSER).body
    links = body.find_all('a', href=re.compile(r'coleccion\.php\?id=\d+'))
    
    for link in links:
        if name in link.text.strip().upper():
            id_manga = int(link['href'].split('=')[1])
            print(f'\t{id_manga}\t{link.text.strip()}')
     
def add_id(id):
    with open(ID_LIST, 'r') as f:
        ids = {int(line.strip()) for line in f}
    
    if int(id) in ids:
        return 0
    else:
        f = open(ID_LIST, 'a')
        status = f.write(f'{id}\n')
        f.close()
        return status

def rm_id(id):
    status = 0
    with open(ID_LIST, "r") as infile, open('id_list.tmp', "w") as outfile:
        # read the file line by line
        for line in infile:
            # check if the line contains the number to delete
            if int(line.strip()) != int(id):
                # write the line to the new file if the number is not found
                outfile.write(line)
            else: 
                status = 1
        
        # replace the original file with the modified file
        os.replace('id_list.tmp', ID_LIST)
        return status

     
# Main program        
while True:
    print("1. Obtain info from ID")
    print("2. Obtain new releases")
    print("3. Search manga")
    print("4. Save new manga id")
    print("5. Delete manga id")
    print("6. Exit")
    print("Enter your choice: ", end="")
    choice = input()

    if choice == "1":
        id = input(ENTER_ID)
        if id == "":
            print("   Error. The ID can't be empty.")
            print("----------------------------------------------")
            continue
        name = manga(id)
        print(f"   Obtained info for {name}. Check the file tomos.txt")
    elif choice == "2":
        mes = input(" * Enter the month: ")
        ano = input(" * Enter the year: ")
        novedades(mes,ano)
    elif choice == "3":
        name = input(" * Enter the name of the manga: ")
        search(name.upper())
    elif choice == "4":
        id = input(ENTER_ID)
        if id == "":
            print("   Error. The ID can't be empty.")
            print("----------------------------------------------")
            continue
        status =  add_id(id)
        if status == 0:
            print("   Error. The ID is already in the list.")
        else:
            print("   Done. The ID has been added to the list.")
    elif choice == "5":
        id = input(ENTER_ID)
        status =  rm_id(id)
        if status == 0:
            print("   Error. The ID wasn't in the list.")
        else:
            print("   Done. The ID has been removed from the list.")  
    elif choice == "6":
        # exit the program
        break
    else:
        print(" ! Invalid choice. Please enter a number from 1 to 6.")

    print("----------------------------------------------")
    