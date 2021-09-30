            
            
                #coding:utf-8
                import time


                code = open("E:/CESI/Projet/ondes/LeCode/data.txt",'r')
                LeCode = code.read()

                def number(donnee):
                    del donnee[1:-14]

                    return donnee

                def trame(number):
                    number.pop(0)
                    number.pop(-1)
                    number.pop(-1)

                    return number


                def octet(trame):

                    trame.pop(0)
                    trame.pop(0)
                    trame.pop(1)
                    trame.pop(4)
                    trame = ''.join(trame)

                    return trame

                LeCode = LeCode.split()
                print(LeCode)
                tampon = []

                for n in range(len(LeCode)):
                    LeCode[n] = list(LeCode[n])
                    tampon.append(octet(trame(number(LeCode[n]))))

                LeCode = tampon

                print("\n",LeCode)

                decimal = []

                for n in range(len(LeCode)):
                    LeCode[n] = list(LeCode[n])
                    tampon = 0
                    puissance = 7

                    for m in range(len(LeCode[n])):

                        if LeCode[n][m] == '1':
                            tampon += 2**puissance

                        puissance = puissance - 1
                    decimal.append(chr(tampon))

                decimal = ''.join(decimal)
                print("\n",decimal)


                time.sleep(500)