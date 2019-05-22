import CifFile

#Het inlezen van een CIF-bestand in een variabele wordt gedaan met de functie:
ciffile = CifFile.ReadCif("bestandsnaam.cif")
#Vervolgens kunnen datablokken worden ingelezen:
datablok = cf["een datablok"]
#Een data-element uit het datablok kan worden gevonden met
data_element = datablok["een datanaam"] 
#Of kan rechtstreeks worden aangesproken met 
data_element = cf["een datablok"]["een datanaam"]
#De data uit een lusblok van het datablok kan worden opgevraagd met  
lb = datablok.GetLoop("een datanaam uit de loop")  
