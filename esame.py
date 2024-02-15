class ExamException(Exception):
    pass

class CSVTimeSeriesFile:
    """
    Una classe per leggere i dati di una serie storica da un file CSV.
    
    Argomenti:
    - name (str): Il nome del file CSV.
    
    Metodi:
    - __init__(self, name): 
        Inizializza l'istanza CSVTimeSeriesFile 
        con il nome del file CSV.
    - get_data(self): 
        Legge i dati dal file CSV e ritorna una lista di liste, 
        dove il primo elemento delle liste è la data 
        ed il secondo il numero di passeggeri. 
    """
    
    def __init__(self, name):
        
        # Setto il nome del file
        self.name = name
        
    def get_data(self):
        
        # Provo ad aprirlo e a leggere le linee 
        try:
            with open(self.name, 'r') as my_file:
                
                lines = my_file.readlines()
                
                # Salto l'intestazione
                lines = lines[1:]
                
                if not lines:
                    return []
            
        except FileNotFoundError:
            raise ExamException(f'Il file {self.name} non esiste')
        except Exception as e:
            raise ExamException(f'Errore in apertura del file: {e}')
        
        # Inizializzo una lista vuota per salvare i dati
        dati = []
        
        old_parts = None
        
        # Leggo il file linea per linea
        for line in lines:
            # Divido la linea sulla virgola
            parts = line.split(',')
            
            # Tolgo gli spazi e gli "a capo"
            parts = [part.strip() for part in parts]
            
            # Controllo che la linea abbia due parti
            if len(parts) < 2:
                # Salto la riga
                continue
            
            # Controllo che ci siano almeno due parti
            if len(parts) > 2:
                # Prendo solo la data e i passeggeri
                parts = parts[:2]
            
            # Controllo che il numero dei passeggeri sia intero
            if not parts[1].isdigit():
                # Salto la linea
                continue
            
            # Controllo che la data sia nel formato YYYY-MM
            if not (len(parts[0]) == 7 and parts[0][:4].isdigit() and parts[0][4] == '-' and parts[0][5:].isdigit()):
                # Salto la riga
                continue
            
            # Definisco l'anno e il mese correnti
            curr_year, curr_month = [int(part) for part in parts[0].split('-')]
            
            # Controllo che il mese sia compreso fra 01 e 12                
            if curr_month < 1 or curr_month > 12:
                # Salto la riga
                continue
            
            if old_parts is not None:
                # Controllo che non ci siano date duplicate
                if parts[0] == old_parts[0]:
                    raise ExamException(f'Ci sono delle date duplicate: {old_parts[0]}, {parts[0]}')
                
                # Controllo che le date siano in ordine
                old_year, old_month = [int(part) for part in old_parts[0].split('-')]
                
                if old_year == curr_year and old_month > curr_month:
                    raise ExamException(f'I mesi delle date non sono in ordine: {old_parts[0]}, {parts[0]}')
                if old_year > curr_year:
                    raise ExamException(f'Gli anni delle date non sono in ordine: {old_parts[0]}, {parts[0]}')
                
            # Assegno la riga corrente alla variabile
            old_parts = parts
            
            # Salva la data e il numero di passeggeri
            date, passengers = parts
            
            # Converti il numero di passeggeri in un intero
            try:
                passengers = int(passengers)
                if passengers <= 0:
                    # Salto la linea
                    continue
            except ValueError:
                # Salto la linea
                continue
            
            # Aggiungo la data e il numero di passeggeri alla lista
            dati.append([date, passengers])
        
        # Ritorno la lista di liste
        return dati


def compute_increments(time_series, first_year, last_year):
    """
    Calcola gli incrementi del numero medio di passeggeri fra coppie di anni consecutivi.
    
    Argomenti:
    - time_series (list): 
        Una lista di liste contenente la serie temporale dei passeggeri.
        Ogni lista interna contiene data e numero di passeggeri.
    - first_year (str): 
        L'anno di inizio dell'intervallo da considerare.
    - last_year (str): 
        L'anno di fine dell'intervallo da considerare.
        
    Ritorno:
    - increments (dict): 
        Un dizionario contenente gli intervalli di due anni come chiavi
        e l'incremento del numero medio di passeggeri rispetto all'anno precedente come valore.
    """
    
    # Controllo che la lista non sia vuota
    if not time_series:
        raise ExamException('Nessun dato valido nel file')
    
    # Controllo che first_year e last_year siano stringhe
    if not isinstance(first_year, str) or not isinstance(last_year, str):
        raise ExamException('first_year e last_year devono essere stringhe')
    
    # Controllo che gli anni abbiano quattro cifre
    if len(first_year) != 4 or len(last_year) != 4:
        raise ExamException('first_year e last_year devono avere quattro cifre')
    
    # Controllo che first_year e last_year siano diversi
    if first_year == last_year:
            raise ExamException('first_year e last_year devono essere diversi')
    
    # Controllo che first_year e last_year siano interi
    if not first_year.isdigit() or not last_year.isdigit():
        raise ExamException('first_year e last_year devono essere stringhe di interi')
    
    # Converti first_year e last_year in interi
    try:
        first_year = int(first_year)
        last_year = int(last_year)
    except ValueError:
        raise ExamException('first_year e last_year devono essere stringhe di interi')
    
    # Controllo che first_year sia minore di last_year
    if first_year > last_year:
        # Poteri invertire gli anni
        # first_year, last_year = last_year, first_year
        raise ExamException('first_year deve essere minore di last_year')
    
    # Se ho due anni e uno dei due non ha dati, ritorno una lista vuota
    first_pass = [el[1] for el in time_series if el[0].startswith(str(first_year))]
    last_pass = [el[1] for el in time_series if el[0].startswith(str(last_year))]
    if first_year + 1 == last_year and (not first_pass or not last_pass):
        return []
    
    # Controllo se first_year e last_year sono presenti nel file
    for year in [first_year, last_year]:
        if str(year) not in [el[0][:4] for el in time_series]:
            raise ExamException(f'L\'anno {year} non è presente nel file')
    
    # Creo un dizionario vuoto per salvare gli incrementi
    increments = {}
    
    prev_avg = 0
    n = 0
    
    # Calcolo gli incrementi
    for year in range(first_year, last_year + 1):
        
        # Conto i mesi e sommo i passeggeri
        curr_count = sum(1 for el in time_series if el[0].startswith(str(year)))
        curr_sum = sum(el[1] for el in time_series if el[0].startswith(str(year)))
        
        # Calcolo l'incremento, se ho almeno un dato
        if curr_count != 0:
            curr_avg = curr_sum / curr_count
            
        # Altrimenti passo all'anno successivo
        else:
            n += 1
            continue
        
        # Se non è il primo anno, salvo l'incremento
        if year > first_year:
            increments[str(year - n - 1) + '-' + str(year)] = curr_avg - prev_avg  
            n = 0
        
        # Assegno la media corrente alla media precedente
        prev_avg = curr_avg
        
    return increments
