======
LOANPY
======

.. image:: https://uc440428f8e04a541624db4fe1a9.previews.dropboxusercontent.com/p/orig/ABFQsCUQqA1IvQ9FlVLMFCAh7EDIfqy3ygUmhvFc5-t6ZZruiFCfNJuDfvqP_rWV2bbd9XVnAvh3ZKs_CmcyKEiDlMXgvYD0TDL9Kpu_nycHFUPHeDSU-tThsSffdQrfdjbjmpTzydGlf8dFSjH5JBxV8kVBSNyz0MjQkHVFxslVbudzZSqHRXl_G7fx7VgRrHe9XKxmh3C6VbpJ7TnDffPiidnNopHp2zQK1om8MTbAzO3nhPUAB0Fmwciz0khCZy0dZf0IsTKbLbSCi7DcE3GYr5JMQQ8vXWURODDCOvtZEEDVxlA-0M8gLjSS6leOeQYU4-FOl0ABTt-Y4MRVR9bX6OwmAA6pav-n_CfIwQP60Ywldxm7lbuuNzsHDMxJvrzcGPubTmCq4KVchGz6KXx5/p.svg?fv_content=true&size_mode=5
   :target: https://pypi.org/project/loanpy/

.. image:: https://about.zenodo.org/static/img/logos/zenodo-gradient-square.svg
   :target: https://zenodo.org/record/4100594#.X5RgbIgzaUk

loanpy is a toolkit for historical linguists. It takes two wordlists as input, one in the recipient language (L1) and one in the tentative donor language (L2) and returns an excel-sheet with a list of potential candidates for loanwords.

Installation
~~~~~~~~~~~~

::

    $ python -m pip install loanpy

Getting started
~~~~~~~~~~~~~~~
1. Import loanfinder module and define global variables
------------------------------------------------------------
::

    >>> from loanpy import loanfinder as lf
    >>> lf.launch()
	
**Parameters:**

- **L1**: str (default="dfhun.csv")
   name the utf-8-encoded csv-dataframe of the borrowing language (L1), in this case Hungarian
- **L2**: str (default="dfgot.csv")
   name the utf-8-encoded csv-dataframe of the tentative donor language (L2), in this case Gothic 
- **L1inputcol**: str (default="root")
   name the column containing the reconstructed roots in the L1-dataframe (in this case dfhun.csv)
- **L2inputcol**: str (default="adapt1")
   name the column containing L2-words adapted to constriants of L1 in the L2-dataframe (in this case dfgot.csv)
- **timelayer**: {str,list,""} (default=["U","FU","Ug"])
   checks which word of the given timelayer appeared last in written documents. Drops all words from the table that appear after that year. Columns "origin" and "year" have to be filled out for this. If you want to skip this, set timelayer=""

**Returns:**

- **lf.dfmatches**: pandas.DataFrame(columns=[*L2inputcol*,"L1_idx"])
   *lf.findphoneticmatches()* appends its output to this global variable and *lf.findloans()* calculates semantic similarities of words stored in it. To view this dataframe, run *lf.dfmatches*. To empty it, rerun *lf.launch()*
 
- **lf.dfL2**: pandas dataframe
   This global variable contains the dataframe of L2 (in this case Gothic). Rows in the column defined in parameter *L2inputcol* containing "too long" or "wrong phonotactics" will be dropped. To view, run *lf.dfL2*   

- **lf.dfL2**: pandas dataframe
   This global variable conatains the dataframe of L1 (in this case Hungarian). Rows in the column defined in parameter *L1inputcol* containing "not old/from L2" will be dropped. To view run *lf.dfL2*

2. Load word vectors
------------------------------

Next, download and unpack 3 Gigabytes of `pretrained Google-News vectors <https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit>`__. These will be needed to calculate the semantic similarity of two given words. Move the file (by default named "GoogleNews-vectors-negative300.bin") to the folder "data", the full path to which can be retrieved via:

::

    >>> import os
    >>> print(os.path.dirname(lf.__file__)+r"\data")

Then run the code below to load the vectors. This process can take several minutes, depending on RAM. Best is to close all unnecessary processes and use a RAM-saving Browser like Opera

::

    >>> lf.loadvectors()

**Paramteres:**

- **filename**: str (default="GoogleNews-vectors-negative300.bin")
   name the file containing the word-vectors

**Returns:**

- **lf.models**: global variable
   serves as input for *hp.gensim_similarity()* and *hp.gensim_synonyms()*
   
	
3. Find loanwords
-------------------

::

    >>> lf.findloans()

**Parameters**:

- **sheetname**: str (must exclude "[]:\*?/\\", default="new")
    results will be written to results.xlsx to a sheet that you can name
- **L1**: str (default="dfhun.csv")
   name the same utf-8-encoded csv-dataframe of L1 that you earlier loaded with lf.launch() 
- **L2**: str (default="dfgot.csv")
   name the same utf-8-encoded csv-dataframe of L2 that you earlier loaded with lf.launch() 
- **L1inputcol**: str (default="root")
   name the same column conatining reconstructed roots that you earlier loaded with lf.launch()
- **semantic_similarity**: function (default=gensim_synonyms)
   name the function that will calculate semantic similarity. Currently there are two options available: *lf.gensim_synonyms* and *lf.gensim_similarity*

**Returns:**

- a new sheet in results.xlsx with potential candidates for loanwords that should be manually evaluated. The sheet will contain a maximum of 500 rows.

Other functions
~~~~~~~~~~~~~~~~~~
adapter.py
----------------------
Import module and define global variables
___________________________________________________
::

   >>> from loanpy import adapter as ad
   >>> ad.launch()

**Parameters**:

- **dfetymology**: str (default="dfetymology.csv")
   name the etymological dictionary of L1, stored as a utf-8 encoded csv-dataframe
- **timelayer**: str (default="")
   name the timelayer in *dfetymology*, from which constraints will be extracted and passed on to the adapt-functions in the form of two variables: *wordstruc* (a list of all possible phonotactic profiles of L1-roots) and *allowedclust* (a list of consonant and vowel clusters occuring in L1-roots). Currently there are three options: "U" (Proto-Uralic), "FU" (Proto-Finno-Ugric), "Ug" (Proto-Ugric). Words with roots in the given timelayer will be kept, while all other rows will be dropped. If timelayer="" all rows will be kept
- **substituteclusters**: str (default="substidict.txt")
   name the txt-file that contains a dictionary the keys of which are L2 consonant and vowel clusters, and values are their possible substitutions in L1. The file was created by the function *clusters2substidict()* and serves as input for *adapt3()*. Iff substiclusters="", the global variables necessary for creating the dictionary will be read from parameters *L2* and *substitutephons* (see below)
- **L2**: str (default="dfgot.csv")
   name the utf-8-encoded csv-dataframe of the tentative donor language (L2), in this case Gothic   
- **substitutephons**: str (default="substi.csv")
   name the csv-table containing L2's phoneme inventory + allophones in column "L2_phons" and their possible substitutions in L1 in column "L1_substitutions". This file is filled out manually beforehand.

**Returns:**

- **ad.dfety**: pandas dataframe
   this global variable contains the information from the etymological dataframe defined in parameter *dfetymology*. Rows below the timecap, that is calculated through the variable *timelayer*, are dropped. To view, run **ad.dfety**

- if parameter *substituteclusters* is not an empty string, following global variables will be defined: 

   - **substidict**: python dictionary
      this global variable contains the dictionary that was defined in variable **substituteclusters** (default="substidict.txt"). To view, run *ad.substidict*

   - **wordstruc**: list
      a list of all possible phonotactic profiles of roots of L1. This is read from the column "old_struc" in *dfetymology*, which in turn is created as part of preprocessing, with the help of *hp.word2struc()*. a phonotactic profile is a string consisting of "C"s (consonants) and "V"s (vowels). To view, run *ad.wordstruc*

   - **maxnrofclusters**: int
      expresses of how many consonant and vowel clusters the longest phonotactic profile in *word2struc* consists. Single consonants and vowels are also counted as clusters, e.g. "CVCV" has 4 clusters ("C", "V", "C", "V"), and "CVCCV" has also 4 ("C", "V", "CC", "V"). This information will be used to ignore L2-words that would be too long for *ad.adapt3()*. To view, run ad.maxnrofclusters

- if parameter *substituteclusters* is an empty string, following global variables will be defined to generate a dictionary that can then serve as input for *substituteclusters*:
   
   - **allowedclust**: set
      a set of all consonant and vowel clusters occuring in L1-roots. To view, run *ad.allowedclust*

   - **maxclustlen**: int
      the highest number of ipa-tokens in any phoneme cluster of all L1-roots. This global variable serves as input for *ad.deletion()*. To view, run *ad.maxclustlen*

   - **dfsubsti**: pandas dataframe
      this global variable contains the dataframe defined in parameter *substitutephons* (default="substi.csv"). *ad.clusters2substidict()* uses this as input. In the future this variable should be kept local and *ad.clusters2substidict()* should take the variable *ad.sudict* as input instead. To view, run *ad.dfsubsti*

   - **sudict**: python dictionary
      this global variable contains *dfsubsti* but stored in the format of a python dictionary. Used by *ad.deletion()*. To view, run *ad.sudict*

   - **dfL2**: pandas dataframe
      contains the dataframe defined in parameter *L2*. To view, run *ad.dfL2*

Create new column with adapted words
_______________________________________________________________________
::

   >>> ad.applyfunc2col(nameofcsv, inputcol, function, outputcol, name)


**Parameters**:

- **nameofcsv**: str (e.g. "dfgot.csv")
   name the utf-8-encoded csv-file in which the column is found to which the function should be applied
- **inputcol**: str (e.g. "substi_in")
   name the column to which the function should be applied
- **function**: function (e.g. *ad.adapt1*, *ad.adapt2*, or *ad.adapt3*)
   name the function that should be applied to the column
- **outputcol**: str (e.g. "adapt1", "adapt2", or "adapt3")
   define how the column should be named where the output is written. Setting the name to an already existing column will overwrite the old one, setting it to a new name will add a new column on the right side of the dataframe
- **name**: str (e.g. "dfgot.csv")
   define under which name you want your file to be saved. Setting the name to an already existing file name will overwrite the old one, setting it to a new name will create a new file.

**Returns:**

- Writes a csv containing a new column with adapted words

Adapt by considering phonemic constraints
___________________________________________________

Summarising the core-periphery model discussed by Paradis and LaCharité (1997: 387) and Chomsky (1986: 147), all constraints of a language apply to loanwords in the core. The more one moves towards the periphery, the less constraints apply. However, "[C]onstraints still active in the outernmost periphery represent absolute constraints. They are responsible for totally prohibited segments such as English English θ and ð in Quebec French". This function adapts loanwords in the outernmost periphery by merely replacing L2-phonemes lacking from L1 by their closest available counterpart.  

::

   >>> ad.adapt1(L2ipa)

**Parameters:**

- **L2ipa**: str
   an L2-word consisting of characters of the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__

**Returns:** str
   L2-phonemes are substituted by the closest available L1-phoneme (substitution manually defined)

**Examples:**
::

   >>> ad.adapt1("bcdhxzɔɛɡɪɸβθl̥m̥n̥r̥aefi")
   pstkssɑækipwtVVVVaefi

**Remarks:**
   before running this, run the code below once, to define the necessary global variables:

::

      >>> ad.launch(substituteclusters="") 

Adapt by considering phonemic and phonotactic constraints
________________________________________________________________________________________

The next function is a step closer towards the periphery, and takes the constraint "phonotactic profile" into account:

::

   >>> ad.adapt2(L2ipa)

**Parameters:**

- **L2ipa**: str
   an L2-word consisting of characters of the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__

**Returns:** str
   the phonotactic profile is adapted by deleting phonemes and inserting "C" and "V" placeholders ("any consonant", "any vowel"). L2-phonemes are substituted by the closest available L1-phoneme (substitution manually defined)

**Examples:**
::

   >>> ad.adapt2("ael")
   'aCelV'

**Remarks:**
   before running this, run the code below once, to define the necessary global variables:

::

      >>> ad.launch(substituteclusters="") 

Adapt by considering phonemic, phonotactic and consonant/vowel cluster constraints
__________________________________________________________________________________________________________________________________________________________________________________________________________________

The second step closer to the core takes phontoactic profile into consideration, and on top it allows only consonant and vowel clusters that are documented in L1
::

   >>> ad.adapt3(L2ipa)

**Parameters:**

- **L2ipa**: str
   an L2-word consisting of characters of the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__

**Returns:** str
   words that have more clusters than *ad.maxnrofclusters* are ignored and "too long" is returned. Else, the string contains all possible combinations of sound substitutions stored in the sound substitution dictionary *ad.substidict*. Only those strings are added to the main outputstring that don't violate the constraint "phonotactic profile", stored in the global variable *ad.wordstruc* and contain only consonant and vowel clusters that were documented in L1, stored in the global variable *ad.allowedclust*

**Examples:**
::

   >>> ad.adapt3("aɣja")
   'aɣa, aja, æɣæ, æjæ'

**Remarks:**
   before running this, run the code below once, to define the necessary global variables:

::

      >>> ad.launch(substituteclusters="") 

Create a dictionary of L1-substitutions for L2-clusters
_______________________________________________________________
::

   >>> ad.clusters2substidict()

**Parameters:**

- **name**: str (default="substidict")
   define the name under which the sound change dictionary should be saved. Leave out the ".txt"-ending because it will be automatically added.

**Returns:** Writes a Python dictionary stored in a ".txt"-file

**Remarks:**
   before running this, run the code below once, to define the necessary global variables:

::

      >>> ad.launch(substituteclusters="") 

Delete phonemes from consonant/vowel clusters
____________________________________________________________
::

   >>> ad.deletion(cluster)

**Parameters:**

- **cluster**: str 
   a string consisting of characters of the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__

**Returns:** str
   a string with sound substituted phonemes, based on different combinatorical options manually defined in *substi.csv*. Only clusters that are documented in L1 are returned

**Examples:**
::

   >>> ad.deletion("trk")
   't, r, k, tk'

   >>> ad.deletion("ŋkj")
   'ŋ, k, j, ŋk, kk'

**Remarks:**
   before running this, run the code below once, to define the necessary global variables:

::

      >>> ad.launch(substituteclusters="") 

reconstructor.py
---------------------
Import module and define global variables
_______________________________________________
::

   >>> from loanpy import reconstructor as rc
   >>> rc.launch()

**Parameters**:

- **soundchangedict**: str (default="scdict_all.txt")
   name the txt-file that contains a dictionary the keys of which are present-day L1 phonemes, and values are their possible roots in the proto-language, stored as regular expressions. The file was created by the function *dfetymology2soundchangedict()* and serves as input for *reconstruct()*. Iff soundchangedict="", the global variables necessary for creating the dictionary will be read from parameters *dfetymology*, **soundsubsti** and *timelayer* (see below)
- **dfetymology**: str (default="dfetymology.csv")
   name the etymological dictionary of L1, stored as a utf-8 encoded csv-dataframe
- **soundsubsti**: str (default="substi.csv")
   name the csv-table containing L2's phoneme inventory + allophones in column "L2_phons" and their possible substitutions in L1 in column "L1_substitutions". This file is filled out manually beforehand.
- **timelayer**: str (default="")
   name the timelayer in dfetymology from which sound changes will be extracted to create the sound change dictionary. Currently there are three options: "U" (Proto-Uralic), "FU" (Proto-Finno-Ugric), "Ug" (Proto-Ugric). Words with roots in the given timelayer will be kept, while all other rows will be dropped. If timelayer="" all rows will be kept

**Returns:**

- if parameter *soundchangedict* is not an empty string, following global variables will be defined:

   - **scdict**: python dictionary
      contains the information from the dictionary defined in the variable *soundchangedict*. To view, run *rc.scdict*

   - **oldprefix**: str
      contains a regex of word initial phonemes and phoneme clusters, that existed in certain L1-roots and disappeared from their respective L1-reflexes. This information is automatically extracted from **scdict**. To view, run *rc.oldprefix*

   - **oldsuffix**: str
      contains a regex of word final phonemes and phoneme clusters, that existed in certain L1-roots and disappeared from their respective L1-reflexes. This information is still manually extracted from **scdict**. To view, run *rc.oldsuffix*

- if parameter *soundchangedict* is an empty string, following global variables will be defined to generate a dictionary of sound changes that can then serve as input for *soundchangedict*. To view, run *rc.soundchangedict*

   - **dfety**: pandas dataframe
      this global variable contains the information from the etymological dataframe defined in parameter *dfetymology*. Rows below the timecap, that is calculated through the variable *timelayer*, are dropped. To view, run **rc.dfety**

   - **substiphons**: str
      a string that contains all phonemes of proto-L1 that could be used to substitute or replicate L1 phonemes. Phonemes that are not in this string will not appear in the sound change dictionary. Note that certain phonemes can be present in the proto-L1 phoneme-inventory but still not be used to substitute any L2 phoneme. Those phonemes are excluded from this variable. To view, run *rc.substiphons*

   - **dfsoundchange**: pandas dataframe
      an empty dataframe to which *ad.getsoundchanges()* appends its output and *fetymology2soundchangedict()* uses as input to create the sound change dictionary


Create new column with reconstructed roots as regular expressions
__________________________________________________________________________

::

   >>> rc.applyfunc2col(nameofcsv, inputcol, function, outputcol, name)

**Parameters**:

- **nameofcsv**: str (e.g. "dfhun.csv")
   name the utf-8-encoded csv-file in which the column is found to which the function should be applied
- **inputcol**: str (e.g. "hun_ipa")
   name the column to which the function should be applied
- **function**: function (e.g. *rc.reconstruct*)
   name the function that should be applied to the column
- **outputcol**: str
   define how the column should be named where the output is written. If you take the name of an already existing column it will be overwritten, if it is a new name, a new column will be added on the right side of the csv
- **name**: str
   define under which name you want your utf-8 file to be saved. Make sure it ends with ".csv". Picking the name of an already existing file will overwrite it, otherwise a new file will be created

**Returns:**

- Writes a csv containing a new column with reconstructed proto-L1 roots, stored as a regular expression

Get soundchanges
_________________________
::

   >>> rc.getsoundchanges(reflex,root)

**Parameters:**

- **reflex**: str (only characterss from the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__)
   a word in the modern-day L1-language, in this case Hungarian

- **root**: str (only characterss from the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__)
   the etymological root of the modern-day word defined in parameter *reflex*

**Returns:** appends a table of soundchanges to *rc.dfsoundchange*

**Remarks:**
   a word-initial "#0" is appended to words that don't start with a consonant. If root and reflex are of different length, the shorter one gets an equal amount of word-final zeros appended. Phonemes not included in *ad.substiclust* are not taken into the dataframe. Before running this, run the code below once, to define the necessary global variables:

::

      >>> rc.launch(soundchangedict="")

Turn an etymological dictionary into a sound change dictionary
_______________________________________________________________________
::

   >>> rc.dfetymology2soundchangedict()

**Parameters:**

- **name**: str (default="scdict")
   pick a name under which the sound change dictionary should be saved. The ending ".txt" will be added automatically.

**Returns:** Writes a txt-file containing a dictionary of sound changes between moder-day L1 and proto-L1

**Remarks:**
   before running this, run the code below once, to define the necessary global variables:

::

      >>> rc.launch(soundchangedict="")
 

Turn a modern-day L1-word into a proto-L1 regex
_________________________________________________________________
::

   >>> rc.reconstruct()

**Parameters:**

- **ipaword**: str (only characters of the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__)
   any modern-day L1 word

**Returns:** str
   if the word contains any phoneme that is not in the sound change dictionary, that phoneme + " not old/from L2" will be returned. Else every phoneme is replaced by its respective dictionary entry, and *rc.oldprefix* and *rc.oldsuffix* are added to the beginning and end

**Examples:**

   >>> rc.reconstruct("loː")
   '^(j|m|s|w|ʃ|C)?(l|C)(e|u|ɑ|o|a|æ|i|V)(((al)(ɑ|o|u|a|æ|e|i))|((ɑ|o|u|a|æ|e|i)(k|r|t)(ɑ|o|u|a|æ|e|i))|((j|m|w|ŋ)(ɑ|o|u|a|æ|e|i)))?$'

**Remarks:**

- Breaking down the above output:

   - *'^(j|m|s|w|ʃ|C)?'*: added word-initially to every word, stored in *rc.oldprefix*. The consonants "j", "m", "s", "w", "ʃ", or any consonant "C" could have word initially existed in the root, and have disappeared in the reflex. "^" marks the beginnin of the string, "?" marks that this character is only optional.

   - *(l|C)*: There must be an "l" or a mandatory placeholder "C". That means that all word-initial modern-day Hungarian "l"s used to be "l"s in the proto-language too. The "C" is only added because *ad.adapt2* ads placeholder "C"s and "V"s to repair the phonotactic structure. Those can be any vowels or consonants, and including these placeholders in the reconstruction makes it possible to find them in the adaptations.

   - *(e|u|ɑ|o|a|æ|i|V)*: One of these must follow the "l". These are all the sounds to which a medial modern-Hungarian "oː" can date back. The "V" is again a placeholder for "any vowel".

   - *(((al)(ɑ|o|u|a|æ|e|i))|((ɑ|o|u|a|æ|e|i)(k|r|t)(ɑ|o|u|a|æ|e|i))|((j|m|w|ŋ)(ɑ|o|u|a|æ|e|i)))?$'*: optional word final phonemes and phoneme clusters that may have existed in the root, but have disappeared in the modern word. "?" denotes the optional search, "$" denotes the end of the string.

- Before running this, run following code to define the necessary global variables:

::

   >>> rc.launch()


helpers.py
-----------------
Import module
_____________________________

::

   >>> from loanpy import helpers as hp

Get phonotactic profile of words
_____________________________________ 
::

   >>> hp.word2struc(ipastring)

**Parameters**:

- ipasring: str
   a string consisting of characters of the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__

**Returns:** str

- a string consisting of "C"s (consonants) and "V"s (vowels)

**Example:**
::

   >>> hp.word2struc("hortobaːɟ")
   "CVCCVCVC"

Divide words into consonant and vowel clusters
_____________________________________________________
::

   >>> hp.ipa2clusters(ipastring)

**Parameters:**

- **ipastring**: str
   a string consisting of characters of the `International Phonetic Alphabet <https://www.internationalphoneticassociation.org/content/full-ipa-chart>`__

**Returns:** list 

- a list of consonant and vowel clusters

**Example:**
::

   >>> hp.ipa2clusters("abauːjkeːr")
   ['a', 'b', 'auː', 'jk', 'eː', 'r']

Turn a list into a regular expression
________________________________________
::

   >>> hp.list2regex(sclist)

**Parameters:**

- **sclist**: list
   a list of strings

**Returns:** str
   a regular expression in form of a string

**Examples:**

::

   >>> hp.list2regex(["b","k","v"])
   "(b|k|v|C)"

   >>> hp.list2regex(["b","k","0","v"])
   "(b|k|v|C)?"

   >>> hp.list2regex(["b","k","0","v","mp"])
   "(b|k|v|mp|C|CC|mC|Cp)?"

   >>> hp.list2regex(["b","k","0","v","mp","mk"])
   "(b|k|v|mp|mk|C|CC|mC|Cp|Ck)?"

   >>> hp.list2regex(["o","ȣ"])
   "(o|ɑ|u|V)"

   >>> hp.list2regex(["ʃʲk"])
   "(ʃʲk|CC|ʃʲC|Ck)"

**Remarks:**

- This function is helping rc.reconstruct() to create a dictionary of sound changes.

- If the list contains at least one consonant, "C" (placeholder for "any consonant") will be added to regex, if it contains at least one vowel, "V" (placeholder for "any vowel") will be added. This is because some L2-words are adapted by inserting an unspecified vowel and consonant ("C" and "V").

- If list contains a zero, it is transformed into a "?" after the regex. This is because a modern L1 sound that can be "0" means it "came out of the void" meaning it is a derivational suffix that appeared later. Therefore it is only optionally included in the regular expression.

- If the list consists of nothing else than one or more zeros, the function returns an empty string. This is because if a modern L1 sound appeared "out of the void" in all cases, it can *only* be a derivational suffix. Therefore it should be excluded from the regex-search

- If the list contains a consonant cluster all combinations of placeholder+actual consonant will be added. "mp" for example would be transformed to "(mp|mC|Cp|CC)". This does not apply to vowel clusters or consonant clusters containing more than two consonants because those didn't exist in Proto-Uralic, Proto-Finno-Ugric or Proto-Ugric.

-  "ȣ" means *any back vowel* ("ɑ", "o", "u"), so all mising back vowels will be added to the regex. Similarly "¨" adds front vowels ("a", "æ", "e", "i") and "ɜ" any vowel ("ɑ", "o", "u", "a", "æ", "e", "i"). This reflects the annotation used by the `Uralic Etymological Dictionary (Uralisches Etymologisches Wörterbuch) <uralonet.nytud.hu>`__

Get editdistance with deletion and insertion only
_________________________________________________________________
::

   >>> editdistancewith2ops(string1, string2)

**Parameters:**

- **string1**, **string2**: str
   two strings between which the edit distance will be calculated

**Returns:** float
   the higher the number the higher the distance between the two strings

**Examples:**
::

   >>> hp.editdistancewith2ops("ajka","Rajka")
   0.4
   
   >>> hp.editdistancewith2ops("Debrecen","Mosonmagyaróvár")
   12.6

**Remarks:**
   The basis for this function comes from ita_c via `geeksforgeeks <https://www.geeksforgeeks.org/edit-distance-and-lcs-longest-common-subsequence/>`__. A weight was added to reflect the *Threshold Principle* formulated by Paradis and LaCharité (1997, p.385), according to which two insertions are cheaper than one deletion: "The problem is really not very different from the dilemma of a landlord stuck with a limited budget for maintenance and a building which no longer meets municipal guidelines. Beyond a certain point, renovating is not viable (there are too many steps to be taken) and demolition is in order. Similarly, we posit that 1) languages have a limited budget for adapting ill-formed phonological structures, and that 2) the limit for the budget is universally set at two steps, beyond which a repair by 'demolition' may apply". So a deletion in this function increases the distance by 1, while an insertion increases it by 0.4

Get up to 20 synonyms
______________________________________

::

	>>> hp.getsynonyms(enword)

**Parameters:**

- **enword**: str
   an English word

- **pos**: str ("n","v","a", "r", or any combination of these e.g. "nv", "ar", "nvr" etc, default= "nvar")
   *pos* stands for "part of speech" of the English word defined in parameter *enword*. The options "n", "v", "a" and "r" stand for "noun", "verb", "adjective", and "anything else", respectively. Any combination of these is allowed too, like "nvar", "nr", "va" etc. 

**Returns:** list
   a list of maximum 20 synonyms of the same part of speech as the input word in *enword*, retrieved from the `Princeton Wordnet <http://wordnetweb.princeton.edu/perl/webwn>`__ via nltk for Python.

**Example:**

::

   >>> hp.getsynonyms("horse","n)
   ['horse','Equus_caballus','gymnastic_horse','cavalry','horse_cavalry','sawhorse','sawbuck','buck','knight']
   

**Remarks:**
   This function is called by *hp.gensim_synonyms()* to find the semantically most similar word pair between two lists of synonyms. 

Find semantically most similar word pair between two lists of synonyms
___________________________________________________________________________________
::

	>>> hp.gensim_synonyms(L1_en, L2_en)

**Parameters:**

- **L1_en**, **L2_en**: str
   Two English words. *L1_en* is the English translation of the L1-word, and *L2_en* the one of the L2-word.

- **posL1**, **posL2**: str ("n","v","a", "r", or any combination of these, default= "nvar")
   these are the respective parts of speech (noun, verb, adjective, or anything else) of the respective input words defined in variables *L1_en* and *L2_en*

**Returns:** float
   the cosine similarity of the most similar synonym's word vectors, calculated with gensim for Python.

**Example:**

   >>> hp.gensim_synonyms("chain","bridge")
   0.31614783

**Remarks:**
   First, a list of synonyms is created for each input word with *hp.getsynonyms()*. Then the Cartesian product of the two lists is taken to calculate the cosine similarity of all possible word pair combinations and the highest similarity score is being returned. If a word is not in *GoogleNews-vectors-negative300.bin*, there is no word vector to calculate the similarity from and the return value is set to -1.

Calculate semantic similarity of two words
_________________________________________________
::

   >>> hp.gensim_similarity(en_word1,en_word2)

**Parameters:**

- **en_word1**, **en_word2**: str
   any two English words, in this case translations of the L1-word and L2-word into English

**Returns:** float
   the cosine similarity of the two words' word vectors, as long as they are included in GoogleNews-vectors-negative300.bin. Phrases have to use an underscore ("_") instead of a space (" ") as separator. 
	
**Example:**

   >>> hp.gensim_similarity("chain", "bridge")
   0.06930015

Data Sources
~~~~~~~~~~~~~~~~~~~~~~~

- **dfhun.csv**: dataframe based on the annex of `Gábor Zaicz's  Hungarian etymological dictionary (2006) <https://regi.tankonyvtar.hu/hu/tartalom/tinta/TAMOP-4_2_5-09_Etimologiai_szotar/adatok.html>`__

- **dfgot.csv**: dataframe based on `Gerhard Köbler's online database of Gothic <https://koeblergerhard.de/wikiling/?f=got>`__

- **dfetymology**: dataframe based on the `Hungarian Academy of Science's online version of Uralisches Etymologisches Wörterbuch <http://uralonet.nytud.hu>`__

- **GoogleNews-vectors-negative300.bin**: `Pretrained word vectors <https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit>`__ based on `word2vec <https://code.google.com/archive/p/word2vec/>`__

Dependencies
~~~~~~~~~~~~~~~~~~~

- **gensim**

- **Levenshtein**

- **pandas**

- **nltk**

- **lingpy**

License
~~~~~~~~~~~~~~~~

Academic Free License (AFL)