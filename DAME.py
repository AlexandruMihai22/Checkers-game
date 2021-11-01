import time
import copy
from collections import namedtuple
from enum import IntEnum

Move = namedtuple('Move', ('jucator', 'pozitie_initiala', 'pozitie_finala'))


class afisare:

    # Primește mutările posibile ca să verifficam dacă jucătorul poate muta într-o anumită poziție
    def mutare(self, stare, mutari_posibile):

        start = time.time()

        while True:

            print("Introdu Coordonate piesă și coordonate mutare (linie_1 coloana_1 linie_2 coloana_2).")
            print("Scrie exit dacă vrei să abandonezi.")

            linie = input()

            if linie == 'exit':
                return None

            try:
                linie1, coloana1, linie2, coloana2 = map(int, linie.split())
            except ValueError:
                print("Coordonate Invalide! Încearcă din Nou! (Nu sunt numere de la 0-7)\n")
                continue

            pozitie1 = (linie1, coloana1)
            pozitie2 = (linie2, coloana2)

            mutare = Move(stare.j_curent, pozitie1, pozitie2)

            if mutare not in mutari_posibile:
                print("Mutare Invalidă! Încearcă din Nou!\n")
                continue

            end_time = time.time()
            print("Jucătorul s-a gândit: %s secunde." % (end_time - start))

            return mutare


class Piesa(IntEnum):
    GOL = 0
    NEGRU = 1
    ALB = 2
    REGE_NEGRU = 3
    REGE_ALB = 4

    # Afișare piese
    def __str__(self):
        if self == self.NEGRU:
            return '○'
        if self == self.ALB:
            return '●'
        if self == self.REGE_NEGRU:
            return 'N'
        if self == self.REGE_ALB:
            return 'A'
        # Celula Goală
        return ' '

    # întoarce culoarea piesei
    def player(self):
        if self == self.NEGRU or self == self.REGE_NEGRU:
            return "NEGRU"
        return "ALB"

    # Dacă piesa e rege sau nu
    def e_rege(self):
        if self == self.REGE_NEGRU or self == self.REGE_ALB:
            return True
        return False


class Joc:
    JMIN = None
    JMAX = None

    def __init__(self, tabla=None):  # Joc()
        if tabla is not None:
            self.matrice = tabla
        else:
            self.matrice = []
            for i in range(8):
                linie = []
                for j in range(8):
                    linie.append(Piesa.GOL)
                self.matrice.append(linie)

            # adaug piesele pe poziții
            for linie in range(3):
                for coloana in range((linie + 1) % 2, 8, 2):
                    self.matrice[linie][coloana] = Piesa.ALB

                for coloana in range(linie % 2, 8, 2):
                    self.matrice[7 - linie][coloana] = Piesa.NEGRU

    # returneaza culoarea celuilalt jucator
    @classmethod
    def jucator_opus(cls, jucator):
        if jucator == cls.JMIN:
            return cls.JMAX
        else:
            return cls.JMIN

    def scor(self):
        regi_negri = 0
        regi_albi = 0
        piese_negre = 0
        piese_albe = 0

        for linie, coloana in self.lista_pozitii_piese_jucator("NEGRU"):
            piece = self.matrice[linie][coloana]
            if piece.e_rege():
                regi_negri += 1
            else:
                piese_negre += 1

        for linie, coloana in self.lista_pozitii_piese_jucator("ALB"):
            piece = self.matrice[linie][coloana]
            if piece.e_rege():
                regi_albi += 1
            else:
                piese_albe += 1

        return (2 * regi_negri + piese_negre) - (2 * regi_albi + piese_albe)

    def scor_2(self):
        return self.nr_piese("NEGRU") - self.nr_piese("ALB")

    def nr_piese(self, jucator):
        suma = 0
        for _ in self.lista_pozitii_piese_jucator(jucator):
            suma += 1

        return suma

    def lista_pozitii_piese_jucator(self, jucator):
        lista = []
        matrice = self.matrice
        for linie, sir in enumerate(matrice):
            for coloana, piesa in enumerate(sir):
                # Dacă am o piesă în acea poziție și dacă e de culoarea jucătorului
                if piesa != Piesa.GOL and piesa.player() == jucator:
                    lista.append([linie, coloana])

        return lista

    def mutari_posibile_jucator(self, jucator):
        mutari = []

        # Selectăm toate piesele jucătorului și facem toate mutările posibile
        for linie, coloana in self.lista_pozitii_piese_jucator(jucator):
            miscari_simple, miscari_puncte = self.mutari_posibile_piesa(jucator, linie, coloana)
            mutari += miscari_simple
            mutari += miscari_puncte

        return mutari

    def mutari_posibile_piesa(self, jucator, linie, coloana):

        piesa = self.matrice[linie][coloana]
        pozitie_curenta = (linie, coloana)
        jucator_opus = self.jucator_opus(jucator)

        # Definim cum se poate mișca piesa
        if piesa.e_rege():
            miscari_permise = (-1, 1)
        else:
            # Alb crește linia
            if jucator == "ALB":
                miscari_permise = (1,)
            else:
                # Negru scade linia
                miscari_permise = (-1,)

        # Mișcările care găsesc celule goale
        miscari_simple = []
        # Mișcări care găsesc piese ale oponentului
        miscari_puncte = []

        for mutare in miscari_permise:
            linie_noua = linie + mutare

            # Dacă avem loc pe tablă
            if not (0 <= linie_noua <= 7):
                continue

            for coloane_posibile in (-1, 1):
                coloana_noua = coloana + coloane_posibile

                # Dacă avem loc pe tablă
                if not (0 <= coloana_noua <= 7):
                    continue

                pozitie_noua = (linie_noua, coloana_noua)
                piesa_poz_noua = self.matrice[linie_noua][coloana_noua]

                # Dacă avem celulă goală
                if piesa_poz_noua == Piesa.GOL:
                    miscari_simple.append(Move(jucator, pozitie_curenta, pozitie_noua))

                # Dacă capturăm piese oponent
                # Trebuie după să verificăm dacă putem să sărim peste piesa oponentului si să găsim o celulă goală
                elif piesa_poz_noua.player() == jucator_opus:
                    linie_oponent = linie_noua + mutare
                    coloana_oponent = coloana_noua + coloane_posibile
                    pozitie_dupa_captura = (linie_oponent, coloana_oponent)

                    # să nu depășim limitele tablei și celula să fie goală
                    if 0 <= linie_oponent <= 7 and 0 <= coloana_oponent <= 7:
                        aux = self.matrice[linie_oponent][coloana_oponent]
                        if aux == Piesa.GOL:
                            miscari_puncte.append(Move(jucator, pozitie_curenta, pozitie_dupa_captura))

        return miscari_simple, miscari_puncte

    def modificare_dupa_mutare(self, mutare):

        jucator, (linie1, coloana1), (linie2, coloana2) = mutare

        # Facem o copie a matricei inițiale
        copie_matrice = copy.deepcopy(self.matrice)

        # Mutăm piesa în copie_tabla
        copie_matrice[linie2][coloana2] = self.matrice[linie1][coloana1]
        copie_matrice[linie1][coloana1] = Piesa.GOL

        # Facem verificăm să vedem dacă piesele au devenit regi
        if jucator == "NEGRU" and linie2 == 0:
            copie_matrice[linie2][coloana2] = Piesa.REGE_NEGRU
        if jucator == "ALB" and linie2 == 7:
            copie_matrice[linie2][coloana2] = Piesa.REGE_ALB

        # Daca e mutarea compusă (am prins o piesă a oponentului)
        if abs(coloana2 - coloana1) > 1:
            mutare = True
        else:
            mutare = False

        # Dacă e mutare compusă (am prins o piesa a oponentului), trb să ștergem piesa oponentului
        if mutare:
            linie = (linie1 + linie2) // 2  # // diviziune fără rest
            coloana = (coloana1 + coloana2) // 2
            copie_matrice[linie][coloana] = Piesa.GOL

        return copie_matrice

    def estimeaza_scor_1(self, adancime):
        t_final = self.final()
        i = -1
        if self.JMAX =="NEGRU":
            i = 1
        if t_final == self.__class__.JMAX:
            return 99 + adancime
        elif t_final == self.__class__.JMIN:
            return -99 - adancime
        else:
            return self.scor()*i

    def estimeaza_scor_2(self, adancime):
        t_final = self.final()
        i = -1
        if self.JMAX =="NEGRU":
            i = 1
        if t_final == self.__class__.JMAX:
            return 99 + adancime
        elif t_final == self.__class__.JMIN:
            return -99 - adancime
        else:
            return self.scor_2()*i

    def final(self):
        if self.nr_piese(self.JMIN) == 0:
            return self.JMAX
        elif self.nr_piese(self.JMAX) == 0:
            return self.JMIN
        else:
            return False

    def lista_mutari(self, jucator):
        l_mutari = []
        mutari_posibile_jucator = self.mutari_posibile_jucator(jucator)
        for mutare in mutari_posibile_jucator:
            l_mutari.append(Joc(self.modificare_dupa_mutare(mutare)))
        return l_mutari

    def __str__(self):
        sir =""
        sir +=  " " + ' '.join(str(i) for i in range(8))
        sir += "\n"
        for i, linie in enumerate(self.matrice):
            sir += str(i) + ' '.join(str(piesa) for piesa in linie)
            sir += "\n"
        return sir

class Stare:

    def __init__(self, tabla, j_curent, adancime, parinte=None, estimare=None):
        self.tabla = tabla
        self.lant = False  # True daca jucătorul poate să captureze mai multe piese
        self.piesa_lant = None  # piesă care face parte din lanț, la care am ajuns
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # estimarea favorabilitatii starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.estimare = estimare

        # lista de mutari posibile (tot de tip Stare) din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        # e de tip Stare (cel mai bun succesor)
        self.stare_aleasa = None


    def mutari(self):
        # lista de informatii din nodurile succesoare
        l_mutari = self.tabla.lista_mutari(self.j_curent)

        juc_opus = Joc.jucator_opus(self.j_curent)

        # mai jos calculam lista de noduri-fii (succesori)
        l_stari_mutari = [
            Stare(mutare, juc_opus, self.adancime - 1, parinte=self)
            for mutare in l_mutari
        ]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla) + "(Joc curent:" + self.j_curent + ")\n"
        return sir


def min_max(stare):
    # daca sunt la o frunza in arborele minimax sau la o stare finala
    if stare.adancime == 0 or stare.tabla.final():
        stare.estimare = stare.tabla.estimeaza_scor_1(stare.adancime)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutariCuEstimare = [
        min_max(x) for x in stare.mutari_posibile
    ]  # expandez(constr subarb) fiecare nod x din mutari posibile

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu estimarea maxima
        stare.stare_aleasa = max(mutariCuEstimare, key=lambda x: x.estimare)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu estimarea minima
        stare.stare_aleasa = min(mutariCuEstimare, key=lambda x: x.estimare)

    stare.estimare = stare.stare_aleasa.estimare
    return stare


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla.final():
        stare.estimare = stare.tabla.estimeaza_scor_1(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()

    if stare.j_curent == Joc.JMAX:
        estimare_curenta = float("-inf")

        for mutare in stare.mutari_posibile:
            # calculeaza estimarea pentru starea noua, realizand subarborele
            stare_noua = alpha_beta(
                alpha, beta, mutare
            )  # aici construim subarborele pentru stare_noua

            if estimare_curenta < stare_noua.estimare:
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if alpha < stare_noua.estimare:
                alpha = stare_noua.estimare
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        estimare_curenta = float("inf")
        for mutare in stare.mutari_posibile:
            # calculeaza estimarea
            stare_noua = alpha_beta(
                alpha, beta, mutare
            )  # aici construim subarborele pentru stare_noua

            if estimare_curenta > stare_noua.estimare:
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if beta > stare_noua.estimare:
                beta = stare_noua.estimare
                if alpha >= beta:
                    break

    stare.estimare = stare.stare_aleasa.estimare

    return stare


def main():
    # Alegere Dificultate
    adancime_max = None
    while adancime_max is None:
        print("Alege Nivelul de Dificultate: ")
        print("1. Ușor\n2. Mediu\n3. Greu\n")

        alegere = int(input())

        if alegere == 1:
            adancime_max = 1
        else:
            if alegere == 2:
                adancime_max = 3
            else:
                if alegere == 3:
                    adancime_max = 7
                else:
                    print("Alegere Invalidă! Introdu din nou!\n")

    # Alegere Algoritm
    global tip_algoritm
    raspuns_valid = False
    while not raspuns_valid:
        tip_algoritm = input(
            "Algoritmul folosit? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-beta\n "
        )
        if tip_algoritm in ["1", "2"]:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta corecta.")

    # Alegere Culoare Piese de Joc

    while Joc.JMIN is None:
        print("\nAlege Culoarea:")
        print("1. Negru\n2. Alb\n")

        alegere = int(input())

        if alegere == 1:
            Joc.JMIN = "NEGRU"
            Joc.JMAX = "ALB"
        else:
            if alegere == 2:
                Joc.JMIN = "ALB"
                Joc.JMAX = "NEGRU"
            else:
                print("Alegere Invalidă! Introdu din nou!\n")

    print("\nAți ales: ", Joc.JMIN)
    print("Computerul joaca cu: ", Joc.JMAX)

    # --------------------------------------------------------------------------

    interfata = afisare()

    castigator = None
    # Generare Stare Inițială Joc
    tabla_curenta = Joc()
    stare_curenta = Stare(tabla_curenta, "NEGRU", adancime_max)  # a tablei de joc
    stare_curenta.j_curent = "NEGRU"
    nr_mutari = 0
    start_time = time.time()

    while True:
        nr_mutari += 1
        print("\nScor NEGRU:", stare_curenta.tabla.scor())
        print("Scor ALB:", (-1) * stare_curenta.tabla.scor())
        print(str(stare_curenta))

        # Verific stările finale
        if stare_curenta.tabla.nr_piese(Joc.JMAX) == 0:
            castigator = Joc.JMIN
            break

        if stare_curenta.tabla.nr_piese(Joc.JMIN) == 0:
            castigator = Joc.JMAX
            break

        mutari_posibile = stare_curenta.tabla.mutari_posibile_jucator(stare_curenta.j_curent)

        # Daca nu mai exista mutari posibile
        if not mutari_posibile:
            # castigator ramane None -> remiză
            break

        # Mutare Om
        if stare_curenta.j_curent == Joc.JMIN:
            mutare = interfata.mutare(stare_curenta, mutari_posibile)

            # pt Exit
            if mutare is None:
                break

            stare_curenta.tabla.matrice = stare_curenta.tabla.modificare_dupa_mutare(mutare)
        # Mutare PC
        else:
            print("\nComputerul se gândește...")

            start = int(round(time.time() * 1000))
            if tip_algoritm == "1":
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm==2
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)

            stare_curenta.tabla = stare_actualizata.stare_aleasa.tabla

            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta))

            end_time = int(round(time.time() * 1000))

            print("Calculatorul s-a gândit: %s secunde." % (end_time - start))

        # Verificăm dacă jucătorul curent poate să facă mai multe mutări consecutive
        # Altfel, e rândul celuilalt jucător
        if not stare_curenta.lant:
            stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)

    if castigator is None:
        print("\nRemiză\n")
    else:
        print("\n Câștigător: ", castigator)

    print("\nScor NEGRU:", stare_curenta.tabla.scor())
    print("Scor ALB:", (-1) * stare_curenta.tabla.scor())

    print("\nJocul s-a terminat după: %s mutări." % str(nr_mutari))
    print("Jocul s-a terminat după: %s secunde." % (time.time() - start_time))


if __name__ == '__main__':
    main()
