
from .datawrangle import MorphDataType, load_dataset

class Language:
    def __init__(self, iso: str):
        # TODO: change assert to Exception

        assert(len(iso)==3)
        self.iso = iso
        self.data = {}


    def _load_datatype(self, datatype: MorphDataType):
        if datatype not in self.data:
            self.data[datatype] = load_dataset(self.iso, datatype)
        return self.data[datatype] is not None

    def inflect(self, word: str, *, features=None):
        
        if not self._load_datatype(MorphDataType.INFLECTIONS):
            return ""
            # throw Exception("Hey u don't have any inflections lol")

        inflects = self.data[MorphDataType.INFLECTIONS]
        if features is None:
            result = inflects[inflects.lemma == word]
        else:
            result = inflects[(inflects.lemma == word) & (inflects.features == features)]
        return result

    def derive(self, word: str, *, morph=None):
        if not self._load_datatype(MorphDataType.DERIVATIONS):
            return None
        # throw Exception("Hey u don't have any inflections lol"):
        derivs = data[MorphDataType.DERIVATIONS]
        if morph is None:
            result = derivs[derivs.lemma == word]
        else:
            result = derivs[(derivs.lemma == word) & (derivs.morph == morph)]
        return result


    def _analyze_word_datatype(self, word: str, datatype: MorphDataType):
        if not self._load_datatype(datatype):
            return ""
        forms = self.data[datatype]
        return forms[forms.form == word].to_csv(sep="\t", index=False, header=None)

    def analyze(self, word: str, *, with_segmentations=False, with_derivations=False, all=True, derivations=False, segmentations=False):

        if all:
            with_segmentations=True
            with_derivations=True

        result = ""

        if derivations:
            # only derivational analyses
            return self._analyze_word_datatype(word, MorphDataType.DERIVATIONS)
        if segmentations:
            # only analyses with segmentations
            return self._analyze_word_datatype(word, MorphDataType.SEGMENTATIONS)
        elif not (with_segmentations or with_derivations):
            # behave as before
            return self._analyze_word_datatype(word, MorphDataType.INFLECTIONS)

        if with_segmentations:
            #result += "Inflectional analysis with segmentation:\n"
            result += self._analyze_word_datatype(word, MorphDataType.SEGMENTATIONS)
        
        #result += "Inflectional analysis, segmentation not available:\n"
        result += self._analyze_word_datatype(word, MorphDataType.INFLECTIONS)

        if with_derivations:
            #result += "Derivational analysis:\n"
            result += self._analyze_word_datatype(word, MorphDataType.DERIVATIONS)

        return result

    def inflections(self):
        self._load_datatype(MorphDataType.INFLECTIONS)
        return self.data[MorphDataType.INFLECTIONS]

    def derivations(self):
        self._load_datatype(MorphDataType.DERIVATIONS)
        return self.data[MorphDataType.DERIVATIONS]

    def segmentations(self):
        self._load_datatype(MorphDataType.SEGMENTATIONS)
        return self.data[MorphDataType.SEGMENTATIONS]
