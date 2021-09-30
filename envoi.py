    #coding:utf-8
            #///////////////////////IMPORT DES MODULES////////////////////////////////////////////////////////
            import pygame
            import wave
            import math
            import binascii
            import socket
            import time

            #//////////////////////////////PARTIE SOCKET///////////////////////////////////////////////////////

            host, port = ('localhost',5566)

            socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            #/////////////////////COMPOSITION DES TRAMES//////////////////////////////////////////////////////

            def decoupage(sequence,nb): # découpage de la données en octets

                sequence = str(sequence)
                segments = []

                while len(sequence)%nb != 0:
                    sequence = sequence + '0'
                    print("WARNING, ajout de bit de bourrage")

                for i in range(0,len(sequence),nb):
                    segments.append(sequence[i:i+nb])

                return segments

            def hamming(decoupage): # ajout du code correcteur de hamming sur nos octets

                if type(decoupage) != list:
                    tmp = []
                    for i in range(len(decoupage)):
                        tmp.append(int(decoupage[i]))
                    decoupage = tmp

                decoupage.insert(0,1) # insertion bit de contôle 1
                decoupage.insert(1,1) # insertion bit de contrôle 2
                decoupage.insert(3,1) #insertion bit de contrôle 4
                decoupage.insert(7,1) # insertion bit de control 8

                if (decoupage[2]+decoupage[4]+decoupage[6]+decoupage[8]+decoupage[10])%2 == 0:
                    decoupage[0] = 0

                if (decoupage[2]+decoupage[5]+decoupage[6]+decoupage[9]+decoupage[10])%2 == 0:
                    decoupage[1] = 0

                if (decoupage[4]+decoupage[5]+decoupage[6]+decoupage[11])%2 == 0:
                    decoupage[3] = 0

                if (decoupage[8]+decoupage[9]+decoupage[10]+decoupage[11])%2 == 0:
                    decoupage[7] = 0

                return decoupage

            def numeroDeTrame(data,donnee):

                number = 0

                while 2**number < len(donnee)/8:
                    number +=1

                liste = list(data)
                n=2**number
                x = bin(n)[2:]
                c = bin(b)[2:]

                liste_a = list(c)
                liste.insert(0,c)

                chaine = ''.join(str(i) for i in liste)
                chaine = chaine.zfill((len(data)+number))
                return list(chaine)

            def rs232(hamming): # application du protocole rs232 + ajout N° de trame

                hamming.insert(len(hamming)+2,0)     # ajout du bit de parité
                if hamming.count(1)%2 == 0:
                    hamming[-1] = 0
                else:
                    hamming[-1] = 1

                hamming.insert(0,1)                  # ajout du bit de start
                hamming.insert(len(hamming)+2,1)     # ajout du bit de stop

                if hamming[1] == '1':
                    hamming[0] = 0
                elif hamming[1] == '0':
                    hamming[0] = 1

                if hamming[-2] == '1':
                    hamming[-1] = 0
                elif hamming[-2] == '0':
                    hamming[-1] = 1

                hamming = ''.join(str(i) for i in hamming)
                return hamming

            def StrBin(texte):

                binaire = []
                for n in texte:
                    binaire.insert(len(binaire)+1,bin(ord(n))[2:])

                    while len(binaire[-1]) < 8:
                        binaire[-1] = '0' + binaire[-1]

                binaire = ''.join(binaire)
                return binaire

            #programme principal
            config = open("E:/CESI/Projet/ondes/LeCode/config.txt","r")
            texte = config.read()
            print("\nVotre texte est : ",texte)
            texte = StrBin(texte)

            segments = decoupage(texte,8)
            b = 1
            for t in range(len(segments)):

                segments[t] = hamming(segments[t])
                segments[t] = numeroDeTrame(segments[t],texte)
                segments[t] = rs232(segments[t])
                print("\n",segments[t])
                b +=1
            try:
                socket.connect((host,port))
                print("\nvous êtes connecté au serveur ;")
                data = ' '.join(segments)
                data = data.encode("utf8")
                socket.sendall(data)
            except:
                print("\nconnexion au serveur échouée :(")
            finally:
                socket.close()

            #///////////////////////////PARTIE GÉNÉRATION DU SON/////////////////////////////////////////

            Donnee = ''.join(segments)
            TroisBits = decoupage(Donnee,3)

            print("\nCréation d'un fichier audio au format WAV (PCM 8 bits mono 8000 Hz)")

            NomFichier = 'son.wav'
            Monson = wave.open(NomFichier,'w') # instanciation de l'objet Monson

            nbCanal = 1    # mono
            nbOctet = 1    # taille d'un échantillon : 1 octet = 8 bits
            fech = 8000   # fréquence d'échantillonnage

            frequence = float(input('\nFréquence du son(Hz) ? '))
            niveau = 1              #float(input('Niveau du son du canal de gauche (0 à 1) ? '))

            nbEchantillon = int(len(Donnee)/3)

            parametres = (nbCanal,nbOctet,fech,nbEchantillon,'NONE','not compressed')# tuple
            Monson.setparams(parametres)    # création de l'en-tête (44 octets)

            print('\nVeuillez patienter...')

            amplitude = 0
            phi = 0

            for i in range(0,nbEchantillon):

                if TroisBits[i][2] == '0':     #####################
                    phi = 0                  # Modulation de Phase
                else:
                    phi = math.pi/2          #####################

                if TroisBits[i][0:2] == '00':            ###########################
                    amplitude = 127.5*niveau*0.25
                elif TroisBits[i][0:2] == '01':
                    amplitude = 127.5*niveau*0.5       # Modulation d'amplitude
                elif TroisBits[i][0:2] == '10':
                    amplitude = 127.5*niveau*0.75
                elif TroisBits[i][0:2] == '11':
                    amplitude = 127.5*niveau*1.0       ############################


                valG = wave.struct.pack('B',int(128+amplitude*math.sin(2.0*math.pi *frequence *i/fech + phi)))
                Monson.writeframes(valG) # écriture frame

            Monson.close()

            print("\nFichier son crée.\nNombre d'échantillons : {}\nFréquence d'échantillonage : {}\nDurée du son : {}".format(nbEchantillon,fech,nbEchantillon/fech))

            #//////////////////////////PARTIE LECTURE DU SON////////////////////////////////////////////////////////////////////////////

            pygame.mixer.init()
            pygame.mixer.Sound("son.wav").play()
            while pygame.mixer.get_busy():
                # lecture en cours
                pass



            time.sleep(500)
          
        