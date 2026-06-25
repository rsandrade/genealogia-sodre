const NODES_DATA = [
  {
    "data": {
      "id": "fernando",
      "label": "Dom Fernando Sodré Pereira",
      "dates": "",
      "category": "historical",
      "generation": 0,
      "note": "Pai de Jerônimo I",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "jeronimo_i",
      "label": "Jerônimo Sodré Pereira I",
      "dates": "1631–1711",
      "category": "historical",
      "generation": 1,
      "note": "Águas Belas, Lisboa → Salvador/BA · ≠ Jerônimo II",
      "spouse": "francisca"
    }
  },
  {
    "data": {
      "id": "francisca",
      "label": "Dona Francisca de Aragão",
      "dates": "",
      "category": "historical",
      "generation": 1,
      "note": "1ª esposa de Jerônimo I",
      "spouse": "jeronimo_i"
    }
  },
  {
    "data": {
      "id": "maria_azevedo",
      "label": "Maria de Azevedo",
      "dates": "",
      "category": "historical",
      "generation": 1,
      "note": "2ª esposa de Jerônimo I",
      "spouse": "jeronimo_i"
    }
  },
  {
    "data": {
      "id": "coronel",
      "label": "Francisco Maria Sodré Pereira",
      "dates": "",
      "category": "barao",
      "generation": 2,
      "note": "Coronel · Filho de Francisco Álvaro",
      "spouse": "meneses"
    }
  },
  {
    "data": {
      "id": "meneses",
      "label": "Maria Ana de Meneses",
      "dates": "",
      "category": "barao",
      "generation": 2,
      "note": "Esposa do coronel",
      "spouse": "coronel"
    }
  },
  {
    "data": {
      "id": "barao",
      "label": "Francisco Pereira Sodré, Barão de Alagoinhas",
      "dates": "1818–1882",
      "category": "barao",
      "generation": 3,
      "note": "Cachoeira/BA · Título: Barão com honra de Grandeza (1879)",
      "spouse": "cora"
    }
  },
  {
    "data": {
      "id": "cora",
      "label": "Cora César Coutinho",
      "dates": "1819–1880",
      "category": "barao",
      "generation": 3,
      "note": "Baronesa · casam. 1834",
      "spouse": "barao"
    }
  },
  {
    "data": {
      "id": "jeronimo_ii",
      "label": "Jerônimo Sodré Pereira II",
      "dates": "~1835",
      "category": "barao",
      "generation": 4,
      "note": "Filho do Barão · Médico, Deputado · ≠ patriarca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "conselheiro",
      "label": "Francisco Maria Sodré Pereira",
      "dates": "1836–1903",
      "category": "barao",
      "generation": 4,
      "note": "Conselheiro · Filho do Barão · Deputado federal BA 1891–1902",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "jose_lino",
      "label": "José Lino Coutinho Sodré Pereira",
      "dates": "",
      "category": "barao",
      "generation": 4,
      "note": "Filho do Barão",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "elisa_barao",
      "label": "Elisa Sodré Pereira",
      "dates": "bat. 1881",
      "category": "barao",
      "generation": 4,
      "note": "Filha do Barão",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "manuel",
      "label": "Manuel Sodré",
      "dates": "",
      "category": "colonial",
      "generation": 2,
      "note": "Elo colonial Sodré–Gramilo",
      "spouse": "maria_gramilo"
    }
  },
  {
    "data": {
      "id": "maria_gramilo",
      "label": "Maria Gramilo",
      "dates": "",
      "category": "colonial",
      "generation": 2,
      "note": "Elo colonial Sodré–Gramilo",
      "spouse": "manuel"
    }
  },
  {
    "data": {
      "id": "eduardo",
      "label": "Eduardo Sodré",
      "dates": "",
      "category": "colonial",
      "generation": 3,
      "note": "Filho de Manuel + Maria",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "antonio_p",
      "label": "Antônio Pereira",
      "dates": "",
      "category": "colonial",
      "generation": 2,
      "note": "Elo colonial",
      "spouse": "isabel_g"
    }
  },
  {
    "data": {
      "id": "isabel_g",
      "label": "Isabel Gramilo",
      "dates": "",
      "category": "colonial",
      "generation": 2,
      "note": "Elo colonial",
      "spouse": "antonio_p"
    }
  },
  {
    "data": {
      "id": "tomaz",
      "label": "Tomaz Gramilo Sodré",
      "dates": "~1860",
      "category": "hypothetical",
      "generation": 3,
      "note": "Amargosa/BA · ~4-6 gerações entre Jerônimo I e Tomaz",
      "spouse": "teodora"
    }
  },
  {
    "data": {
      "id": "teodora",
      "label": "Teodora Julia da Cruz",
      "dates": "",
      "category": "hypothetical",
      "generation": 3,
      "note": "Esposa de Tomaz",
      "spouse": "tomaz"
    }
  },
  {
    "data": {
      "id": "marcelo",
      "label": "Marcelo Gramilo Sodré",
      "dates": "1897–1976",
      "category": "confirmed",
      "generation": 4,
      "note": "Casam. 09/02/1924 · Montes Claros/MG · 7 filhos",
      "spouse": "rita_rosa"
    }
  },
  {
    "data": {
      "id": "rita_rosa",
      "label": "Rita Rosa Sodré",
      "dates": "1901–1992",
      "category": "confirmed",
      "generation": 4,
      "note": "7 filhos",
      "spouse": "marcelo"
    }
  },
  {
    "data": {
      "id": "francisco",
      "label": "Francisco Gramilo Sodré",
      "dates": "1925–1999",
      "category": "confirmed",
      "generation": 5,
      "note": "Bat. 17/05/1925 · Casam. 26/12/1953 · Ibitupa/BA",
      "spouse": "atanagilda"
    }
  },
  {
    "data": {
      "id": "atanagilda",
      "label": "Atanagilda Odete dos Santos",
      "dates": "1933–?",
      "category": "confirmed",
      "generation": 5,
      "note": "Bat. 25/06/1933 · Casam. 26/12/1953 · óbito: data incorreta, aguardando confirmação",
      "spouse": "francisco"
    }
  },
  {
    "data": {
      "id": "gervasio",
      "label": "Gervásio Eusébio dos Santos",
      "dates": "",
      "category": "materno",
      "generation": 4,
      "note": "Pai de Atanagilda Odete dos Santos · confirmação oral · possível parente de Francisco Eusébio dos Santos (padrinho em Amargosa, 1895), precisa confirmação documental",
      "spouse": "maria_aleluia"
    }
  },
  {
    "data": {
      "id": "maria_aleluia",
      "label": "Maria Aleluia dos Santos",
      "dates": "",
      "category": "materno",
      "generation": 4,
      "note": "Avó materna · confirmação oral",
      "spouse": "gervasio"
    }
  },
  {
    "data": {
      "id": "francisco_lud",
      "label": "Francisco Ludgero Vaz Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Ramo Vaz Sodré de Amargosa · casou com Olympia Flavia de Miranda Sodré · pessoa distinta de Francisco Gramilo Sodré · possível elo H4, precisa confirmação",
      "spouse": "olympia_f"
    }
  },
  {
    "data": {
      "id": "olympia_f",
      "label": "Olympia Flavia de Miranda Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Esposa de Francisco Ludgero Vaz Sodré · ramo Vaz Sodré de Amargosa",
      "spouse": "francisco_lud"
    }
  },
  {
    "data": {
      "id": "horacio_vs",
      "label": "Horácio Vaz Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Ramo Vaz Sodré de Amargosa · 11 registros de inventário no APEB · hipótese H4 como possível elo, precisa confirmação",
      "spouse": "adelina_mj"
    }
  },
  {
    "data": {
      "id": "adelina_mj",
      "label": "Adelina Maria de Jesus",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Esposa de Horácio Vaz Sodré",
      "spouse": "horacio_vs"
    }
  },
  {
    "data": {
      "id": "amelia_vaz",
      "label": "Amélia Vaz Padri",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filha registrada no ramo Horácio Vaz Sodré + Adelina Maria de Jesus",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "firmino_vs",
      "label": "Firmino Vaz Sodré",
      "dates": "ativo 1909–1914",
      "category": "confirmed",
      "generation": 5,
      "note": "Amargosa/BA · batismo do filho José (31/01/1909) + padrinho em 1914 · relação com Tomaz/Marcelo ainda não confirmada",
      "spouse": "laurinda_s"
    }
  },
  {
    "data": {
      "id": "laurinda_s",
      "label": "Laurinda Sodré",
      "dates": "ativa 1909–1914",
      "category": "confirmed",
      "generation": 5,
      "note": "Esposa de Firmino · mãe de José · madrinha junto com Firmino em 1914",
      "spouse": "firmino_vs"
    }
  },
  {
    "data": {
      "id": "jose_firmino",
      "label": "José Sodré",
      "dates": "bat. 31/01/1909",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho de Firmino Vaz Sodré + Laurinda Sodré · Arraial do Conente, Amargosa",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "esmeraldo_vs",
      "label": "Esmeraldo Vaz Sodré",
      "dates": "ativo 1912–1914",
      "category": "confirmed",
      "generation": 5,
      "note": "Amargosa/BA · pai de Olímpio, Ismael e Anizio · OCR lê \"Euneraldo/Ceneraldo\" · confirmado pelo FamilySearch (ID 6DLV-ZG23) · possível parente de Firmino Vaz Sodré (mesmo sobrenome Vaz Sodré)",
      "spouse": "florinda_a"
    }
  },
  {
    "data": {
      "id": "florinda_a",
      "label": "Florinda de Andrade",
      "dates": "ativa 1912–1914",
      "category": "confirmed",
      "generation": 5,
      "note": "Esposa de Esmeraldo Vaz Sodré · mãe de Olímpio, Ismael e Anizio · OCR lê \"Alarinda\" · confirmada pelo FamilySearch",
      "spouse": "esmeraldo_vs"
    }
  },
  {
    "data": {
      "id": "olimpio_s",
      "label": "Olímpio Sodré",
      "dates": "n. 18/11/1913 · bat. 14/11/1914",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho de Esmeraldo Vaz Sodré + Florinda de Andrade · padrinhos: Firmino + Laurinda · Amargosa/BA · confirmado pelo FamilySearch",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "ismael_s",
      "label": "Ismael Sodré",
      "dates": "bat. 14/11/1914",
      "category": "confirmed",
      "generation": 6,
      "note": "~30 meses no batismo · filho de Esmeraldo Vaz Sodré + Florinda de Andrade · Amargosa/BA",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "anizio_s",
      "label": "Anizio Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho de Esmeraldo Vaz Sodré + Florinda de Andrade · FamilySearch",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "manoel_caetano",
      "label": "Manoel Caetano Sodré",
      "dates": "ativo 1938–1941",
      "category": "confirmed",
      "generation": 5,
      "note": "Pai de Antonia Sodré de Jesus e Luciana Caetana Sodré · casamentos 1938 e 1941 · Amargosa/BA · relação com Firmino/Gramilo ainda não confirmada",
      "spouse": "maria_paulina"
    }
  },
  {
    "data": {
      "id": "maria_paulina",
      "label": "Maria Paulina de Jesus",
      "dates": "ativa 1938–1941",
      "category": "confirmed",
      "generation": 5,
      "note": "Mãe de Antonia e Luciana · OCR lê \"Joares/Podré\" · FamilySearch registra \"de Jesus\"",
      "spouse": "manoel_caetano"
    }
  },
  {
    "data": {
      "id": "antonia_sodre",
      "label": "Antonia Sodré de Jesus",
      "dates": "cas. 10/12/1941",
      "category": "confirmed",
      "generation": 6,
      "note": "Filha de Manoel Caetano Sodré + Maria Paulina de Jesus · casou Vicente Maciel de Almeida (22 anos) · Amargosa/BA",
      "spouse": "vicente_miel"
    }
  },
  {
    "data": {
      "id": "luciana_caetana",
      "label": "Luciana Caetana Sodré",
      "dates": "cas. 01/12/1938",
      "category": "confirmed",
      "generation": 6,
      "note": "Filha de Manoel Caetano Sodré + Maria Paulina de Jesus · casou Pedro Maciel de Almeida (23 anos) · FamilySearch · irmã de Antonia Sodré",
      "spouse": "pedro_maciel"
    }
  },
  {
    "data": {
      "id": "vicente_miel",
      "label": "Vicente Maciel de Almeida",
      "dates": "cas. 10/12/1941",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho de Christino José de Almeida + Jacula Conceição de Almeida · 22 anos · irmão de Pedro Maciel de Almeida",
      "spouse": "antonia_sodre"
    }
  },
  {
    "data": {
      "id": "pedro_maciel",
      "label": "Pedro Maciel de Almeida",
      "dates": "cas. 01/12/1938",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho de Ricardo José de Almeida + Macula Conceição de Almeida · 23 anos · irmão de Vicente Maciel de Almeida",
      "spouse": "luciana_caetana"
    }
  },
  {
    "data": {
      "id": "eufrasio_vs",
      "label": "Eufrásio Victor Sodré",
      "dates": "cas. 04/02/1937",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho de Antonio Victor Sodré + Bastilla Maria de Jesus · casou Firmina Moreira de Freitas · Amargosa/BA",
      "spouse": "firmina_mf"
    }
  },
  {
    "data": {
      "id": "antonio_victor",
      "label": "Antonio Victor Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Pai de Eufrásio Victor Sodré (com Bastilla) e possivelmente de João Gregorio Sodré (com Adelia Maria Sódre, FS fs9) · Amargosa/BA · se confirmado, teve 2 esposas",
      "spouse": "bastilla_mj"
    }
  },
  {
    "data": {
      "id": "bastilla_mj",
      "label": "Bastilla Maria de Jesus",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Mãe de Eufrásio Victor Sodré",
      "spouse": "antonio_victor"
    }
  },
  {
    "data": {
      "id": "firmina_mf",
      "label": "Firmina Moreira de Freitas",
      "dates": "cas. 04/02/1937",
      "category": "confirmed",
      "generation": 6,
      "note": "Esposa de Eufrásio Victor Sodré · mãe: Maria Sodré de Jesus (?) — HIPÓTESE",
      "spouse": "eufrasio_vs"
    }
  },
  {
    "data": {
      "id": "maria_sodre_j",
      "label": "Maria Sodré de Jesus (?)",
      "dates": "",
      "category": "hypothetical",
      "generation": 5,
      "note": "Mãe de Firmina Moreira de Freitas · HIPÓTESE — precisa confirmação",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "clelino_vaz",
      "label": "Clelino Vaz",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Testemunha no casamento 10/12/1941 Amargosa · sobrenome Vaz = possível ramo Vaz Sodré",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "joao_gregorio",
      "label": "João Gregorio Sodré",
      "dates": "n. ~1906 · cas. 1933",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho de Antonio Victor Sodré + Adelia Maria Sódre · casou Maria Magdalena Lopes · Amargosa/Tapera · FS fs9 · se Antonio Victor é o mesmo pai de Eufrásio, então são meio-irmãos",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "francisco_eus",
      "label": "Francisco Eusébio dos Santos",
      "dates": "ativo 1895",
      "category": "materno",
      "generation": 4,
      "note": "Padrinho em batismo em Brejaês, Amargosa (08/12/1895) · possível irmão/parente de Gervásio Eusébio dos Santos — precisa confirmação",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "geruasio_samp",
      "label": "Geruásio José Sampaio",
      "dates": "ativo 1895",
      "category": "hypothetical",
      "generation": 4,
      "note": "Pai em batismo de Maria, Brejaês/Amargosa (08/12/1895) · possível pista para o sobrenome Sampaio — precisa investigação",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "arlindo",
      "label": "Arlindo Gramilo Sodré",
      "dates": "† 31/01/2025",
      "category": "confirmed",
      "generation": 5,
      "note": "8 filhos",
      "spouse": "noemia"
    }
  },
  {
    "data": {
      "id": "noemia",
      "label": "Noemia Rocha Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "8 filhos",
      "spouse": "arlindo"
    }
  },
  {
    "data": {
      "id": "zeca",
      "label": "José Gramilo Sudré (Zeca)",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "9 filhos · Sudré = erro cartorário",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "otavia",
      "label": "Otávia Rosa Sodré Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "10 filhos",
      "spouse": "eustaquio"
    }
  },
  {
    "data": {
      "id": "eustaquio",
      "label": "Eustáquio Eusébio Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "10 filhos",
      "spouse": "otavia"
    }
  },
  {
    "data": {
      "id": "elisa",
      "label": "Elisa Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "3 filhos (Elizabete adotiva, Zeilde, Valdeci/Sísio)",
      "spouse": "alfredo"
    }
  },
  {
    "data": {
      "id": "alfredo",
      "label": "Alfredo Fernandes",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "3 filhos (Elizabete adotiva)",
      "spouse": "elisa"
    }
  },
  {
    "data": {
      "id": "zeilde",
      "label": "Zeilde",
      "dates": "✝",
      "category": "confirmed",
      "generation": 6,
      "note": "falecido",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "valdeci",
      "label": "Valdeci (apelido: Sísio)",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "mãe de Alfredo Neto",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "elizabete",
      "label": "Elizabete",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "filha adotiva (mais velha) · mãe de Cesar",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "alfredo_neto",
      "label": "Alfredo Neto",
      "dates": "",
      "category": "confirmed",
      "generation": 7,
      "note": "Filho de Valdeci (Sísio) · neto de Elisa Gramilo Sodré",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "cesar",
      "label": "Cesar",
      "dates": "",
      "category": "confirmed",
      "generation": 7,
      "note": "Filho de Elizabete",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "tania_karla",
      "label": "Tânia Karla Sodré Bulhões",
      "dates": "",
      "category": "confirmed",
      "generation": 7,
      "note": "Filha de Elizabete · neta de Elisa Gramilo Sodré",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "isabel",
      "label": "Isabel Rosa Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "8 filhos · Itororó-BA",
      "spouse": "maximiliano"
    }
  },
  {
    "data": {
      "id": "maximiliano",
      "label": "Maximiano José de Souza",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "8 filhos · Itororó-BA · veio de Teófilo Otoni (MG) → Aiquara",
      "spouse": "isabel"
    }
  },
  {
    "data": {
      "id": "jovina",
      "label": "Jovina Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Fazenda Babilônia (limítrofe com Fazenda Santa Terezinha)",
      "spouse": "manezinho"
    }
  },
  {
    "data": {
      "id": "manezinho",
      "label": "Manezinho",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Dono da Fazenda Babilônia",
      "spouse": "jovina"
    }
  },
  {
    "data": {
      "id": "etelvina_t",
      "label": "Etelvina Rosa Souza (\"Tezinha\")",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "× Erotildes Ribeiro Sodré · nascida em Aiquara/BA · Filho: Admilson Ribeiro Sodré",
      "spouse": "erotildes"
    }
  },
  {
    "data": {
      "id": "erotildes",
      "label": "Erotildes Ribeiro Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "× Etelvina Tezinha · pais: Manuel Ribeiro Sodré e Mariana Rosa de Jesus",
      "spouse": "etelvina_t"
    }
  },
  {
    "data": {
      "id": "admilson",
      "label": "Admilson Ribeiro Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 7,
      "note": "Filho de Erotildes×Etelvina · nascido em Aiquara/BA",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "valdivino",
      "label": "Valdivino",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "carlos_im",
      "label": "Carlos",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "francisco_im",
      "label": "Francisco",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "dutinha",
      "label": "Dutinha",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Apelido",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "edvaldo",
      "label": "Edvaldo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "lelinha",
      "label": "Lelinha",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Apelido",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "maria_im",
      "label": "Maria",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "mãe de Simone · filhas em Salvador/BA e São Paulo/SP",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "simone",
      "label": "Simone",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Filha de Maria · neta de Isabel Rosa Sodré · Salvador/BA",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "alice_santos",
      "label": "Alice dos Santos",
      "dates": "",
      "category": "confirmed",
      "generation": 4,
      "note": "Irmã de Maria Aleluia · 1ª esposa de Marcos Freire de Andrade · Filhos: Marcos, Marlice, Janete, Marcus Marquinhos, Lígia",
      "spouse": "marcos_andrade"
    }
  },
  {
    "data": {
      "id": "marcos_m",
      "label": "Marcos",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Filho de Marcos×Alice",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "marlice",
      "label": "Marlice",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Filha de Marcos×Alice",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "janete",
      "label": "Janete",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Filha de Marcos×Alice",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "marcus",
      "label": "Marcus \"Marquinhos\"",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Filho de Marcos×Alice",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "ligia",
      "label": "Lígia",
      "dates": "",
      "category": "confirmed",
      "generation": 5,
      "note": "Filha de Marcos×Alice",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "marcos_andrade",
      "label": "Marcos Freire de Andrade",
      "dates": "",
      "category": "confirmed",
      "generation": 4,
      "note": "2 casamentos",
      "spouse": "alice_santos"
    }
  },
  {
    "data": {
      "id": "florenca",
      "label": "Florença Reis Andrade",
      "dates": "",
      "category": "probable",
      "generation": 5,
      "note": "2ª esposa de Marcos",
      "spouse": "marcos_andrade"
    }
  },
  {
    "data": {
      "id": "magno",
      "label": "Magno Reis Andrade",
      "dates": "",
      "category": "probable",
      "generation": 6,
      "note": "Filho de Marcos × Florença",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "ieda",
      "label": "Iêda Reis Andrade",
      "dates": "",
      "category": "probable",
      "generation": 6,
      "note": "Filha de Marcos × Florença",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "magnaldo",
      "label": "Magnaldo Reis Andrade",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "casou com Veralúcia Sodré · separaram ~1990 · Filho de Marcos × Florença",
      "spouse": "veralucia"
    }
  },
  {
    "data": {
      "id": "atanagilda_f",
      "label": "Atanagilda Sodré Sampaio",
      "dates": "1954",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 11/04/1954",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "veralucia",
      "label": "Veralúcia Sodré",
      "dates": "1955",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 30/09/1955",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "luiz_carlos",
      "label": "Luiz Carlos Sudré",
      "dates": "1957",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 30/03/1957 · Sudré = erro cartorário",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "francisco_f",
      "label": "Francisco Gramilo Sodré Filho",
      "dates": "1959",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 26/07/1959 · Professor, PMA",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "angelica",
      "label": "Angélica Maria Sodré Costa",
      "dates": "1961",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 02/03/1961",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "rita_cassia",
      "label": "Rita de Cássia Sodré",
      "dates": "1962",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 09/10/1962",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "djalma",
      "label": "Djalma Gramilo Sodré",
      "dates": "1964",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 15/02/1964",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "paulo_renato",
      "label": "Paulo Renato Sodré",
      "dates": "1965",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 19/06/1965",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "ronaldo",
      "label": "Ronaldo Gramilo Sodré",
      "dates": "1966",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 16/12/1966",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "julio",
      "label": "Júlio César Gramilo Sodré",
      "dates": "1968",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 09/01/1968",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "cristina",
      "label": "Cristina Maria Gramilo Sodré",
      "dates": "1969",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 02/08/1969",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sinara",
      "label": "Sinara Magali Sodré",
      "dates": "1971",
      "category": "confirmed",
      "generation": 6,
      "note": "n. 20/12/1971",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_arleno_gramilo_sodre",
      "label": "Arlenô Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_marcelo_gramilo_sodre_neto",
      "label": "Marcelo Gramilo Sodré Neto",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_arlindo_gramilo_sodre_filho",
      "label": "Arlindo Gramilo Sodré Filho",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_antonio_cesar_silva_sodre",
      "label": "Antonio Cesar Silva Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_luciane_silva_sodre",
      "label": "Luciane Silva Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_cristiane_silva_sodre",
      "label": "Cristiane Silva Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_rita_de_c_ssia_silva_sodre_figueredo",
      "label": "Rita de Cássia Silva Sodré Figueredo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_manoel_ailton_silva_sodre",
      "label": "Manoel Ailton Silva Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de arlindo",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_jose_gramilo_sodre_filho",
      "label": "José Gramilo Sodré Filho",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_walter_gramilo_sodre",
      "label": "Walter Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_jailson_gramilo_sodre",
      "label": "Jailson Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_ivan_gramilo_sodre",
      "label": "Ivan Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_manoelito_gramilo_sodre",
      "label": "Manoelito Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_joselito_gramilo_sodre",
      "label": "Joselito Gramilo Sodré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_cleide",
      "label": "Cleide",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_ione_rosa_sudre",
      "label": "Ione Rosa Sudré",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_maria_rita",
      "label": "Maria Rita",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de zeca",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_geni_bispo",
      "label": "Geni Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_zenito_bispo",
      "label": "Zenito Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_sinval_bispo",
      "label": "Sinval Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_maria_helena_sodre_bispo",
      "label": "Maria Helena Sodré Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_maiza_rosa_bispo_gouveia",
      "label": "Maiza Rosa Bispo Gouveia",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_zelia_bispo",
      "label": "Zélia Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_juvenil_sodre_bispo",
      "label": "Juvenil Sodré Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_nilda_sodre_bispo_de_souza",
      "label": "Nilda Sodré Bispo de Souza",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_antonio_carlos_bispo",
      "label": "Antônio Carlos Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_valdeck_bispo",
      "label": "Valdeck Bispo",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de otavia",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_zeilde",
      "label": "Zeilde",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de elisa",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_valdeci_sisio",
      "label": "Valdeci (Sísio)",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de elisa",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_elizabete",
      "label": "Elizabete",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de elisa",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_t_nia_karla",
      "label": "Tânia Karla",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de elisa",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_cesar",
      "label": "Cesar",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de elisa",
      "spouse": null
    }
  },
  {
    "data": {
      "id": "sob_alfredo_neto",
      "label": "Alfredo Neto",
      "dates": "",
      "category": "confirmed",
      "generation": 6,
      "note": "Filho(a) de elisa",
      "spouse": null
    }
  }
];
