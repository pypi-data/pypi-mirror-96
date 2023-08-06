import faulthandler
import pytest
import pkgutil
import sys


faulthandler.enable(file=sys.stderr, all_threads=True)


def check_if_hfst_is_available():
    # Check that HFST is available
    return pkgutil.find_loader("hfst") is not None


@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_raw_output():

    from estnltk import Text
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import HfstEstMorphAnalyser
    
    # Test HfstEstMorphAnalyser's raw output format
    hfstAnalyser = HfstEstMorphAnalyser( output_format='raw' )

    # Case 1
    input_text_str = 'No, tore talv! Vannaemale ei öeldud, et mäesuusatamine võib-olla tore Juhhhei'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = [ 
       [{'weight': 6.0, 'raw_analysis': 'no+Interj', 'start': 0, 'end': 2}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 2, 'end': 3}], \
       [{'weight': 6.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 4, 'end': 8}], \
       [{'weight': 6.0, 'raw_analysis': 'talv+N+Sg+Nom', 'start': 9, 'end': 13}], \
       [{'weight': 0.0, 'raw_analysis': '!+CLB', 'start': 13, 'end': 14}], \
       [{'weight': float('inf'), 'raw_analysis': None, 'start': 15, 'end': 25}], \
       [{'weight': 1.0, 'raw_analysis': 'ei+Adv', 'start': 26, 'end': 28}, \
        {'weight': 2.0, 'raw_analysis': 'ei+V+Neg', 'start': 26, 'end': 28}], \
       [{'weight': 5.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Prc', 'start': 29, 'end': 35}, \
        {'weight': 6.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Ind+Neg', 'start': 29, 'end': 35}, \
        {'weight': 9.0, 'raw_analysis': 'öeldu+N+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 10.0, 'raw_analysis': 'öeldud+A+Sg+Nom', 'start': 29, 'end': 35}, \
        {'weight': 11.0, 'raw_analysis': 'öeldud+A+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 13.0, 'raw_analysis': 'ütlema+V+Der/tud+A', 'start': 29, 'end': 35}, \
        {'weight': 14.0, 'raw_analysis': 'ütlema+V+Der/tu+A+Pl+Nom', 'start': 29, 'end': 35}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 35, 'end': 36}], \
       [{'weight': 1.0, 'raw_analysis': 'et+CS', 'start': 37, 'end': 39}], \
       [{'weight': 40.0, 'raw_analysis': 'mäesuusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 56.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 66.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatama+V+Der/mine+N+Sg+Nom', 'start': 40, 'end': 54}], \
       [{'weight': 5.0, 'raw_analysis': 'võib-olla+Adv', 'start': 55, 'end': 64}], \
       [{'weight': 6.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 65, 'end': 69}], \
       [{'weight': float('inf'), 'raw_analysis': None, 'start': 70, 'end': 77 }] ]
    assert results == expected_results

    # Case 2
    input_text_str = 'Trinidad ja Tobago olidki saanud suusariigiks'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = [ 
       [{'raw_analysis': 'Trinidad+N+Prop+Sg+Nom', 'end': 8, 'weight': 11.0, 'start': 0}], \
       [{'raw_analysis': 'ja+CC', 'end': 11, 'weight': 0.0, 'start': 9}], \
       [{'raw_analysis': 'Tobago+N+Prop+Sg+Nom', 'end': 18, 'weight': 11.0, 'start': 12}, \
        {'raw_analysis': 'Tobago+N+Prop+Sg+Gen', 'end': 18, 'weight': 12.0, 'start': 12}], \
       [{'raw_analysis': 'olema+V+Pers+Prt+Ind+Pl3+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}, \
        {'raw_analysis': 'olema+V+Pers+Prt+Ind+Sg2+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}], \
       [{'raw_analysis': 'saama+V+Pers+Prt+Prc', 'end': 32, 'weight': 3.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Pers+Prt+Ind+Neg', 'end': 32, 'weight': 4.0, 'start': 26}, \
        {'raw_analysis': 'saanu+N+Pl+Nom', 'end': 32, 'weight': 10.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A', 'end': 32, 'weight': 12.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Sg+Nom', 'end': 32, 'weight': 12.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Pl+Nom', 'end': 32, 'weight': 13.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nu+N+Pl+Nom', 'end': 32, 'weight': 13.0, 'start': 26}], \
       [{'raw_analysis': 'suusk+N+Sg+Gen#riik+N+Sg+Tra', 'end': 45, 'weight': 56.0, 'start': 33}] ]
    assert results == expected_results
    #         
    # *** Test lookup method
    
    # Case 3
    records = hfstAnalyser.lookup('alpimajakene')
    #print(records)
    expected_records = [ \
       {'raw_analysis': 'alpi+Pref#majake+N+Sg+Nom+Use/Rare', 'weight': 84.0}, \
       {'raw_analysis': 'alpi+Pref#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 90.0}, \
       {'raw_analysis': 'alpi+N+Sg+Gen#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 92.0}, \
       {'raw_analysis': 'alp+A+Sg+Nom#imama+V+Der/ja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 110.0}, \
       {'raw_analysis': 'alpi+Guess#majake+N+Sg+Nom+Use/Rare', 'weight': 269.0}, \
       {'raw_analysis': 'alpi+Guess#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 275.0} \
    ]
    assert records == expected_records
    
    # Case 4
    records = hfstAnalyser.lookup('äraguugeldatud') # as in: "Kui Sul on äraguugeldatud, võid tulla kohvi jooma."
    #print(records)
    expected_records = [ \
       {'raw_analysis': 'ära+Adv#guugeldama+V+Der/tud+A', 'weight': 65.0}, \
       {'raw_analysis': 'ära+Adv#guugeldama+V+Der/tu+A+Pl+Nom', 'weight': 66.0} \
    ]
    assert records == expected_records

    # Case 5
    records = hfstAnalyser.lookup('xyxrjxxf3tg5') # totally unknown word
    assert records == []


@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_raw_output_on_multiple_normalized_word_forms():
    from estnltk import Text, Annotation
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import HfstEstMorphAnalyser
    # Test HfstEstMorphAnalyser's raw output format
    hfstAnalyser = HfstEstMorphAnalyser( output_format='raw' )
    # Case 1: word normalizations without unknown words
    text = Text('''isaand kui juuuubbeee ...''')
    text.tag_layer(['compound_tokens', 'words'])
    # Add multiple normalized forms
    for word in text.words:
        if word.text == 'isaand':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['isand', 'issand']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='isand') )
                word.add_annotation( Annotation(word, normalized_form='issand') )
        if word.text == 'juuuubbeee':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['jube']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='jube') )
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = \
    [
      [{'start': 0, 'weight': 7.0, 'raw_analysis': 'isand+N+Sg+Nom', 'end': 6}, 
       {'start': 0, 'weight': 7.0, 'raw_analysis': 'issand+N+Sg+Nom', 'end': 6}], 
      [{'start': 7, 'weight': 2.0, 'raw_analysis': 'kui+CS', 'end': 10}, 
       {'start': 7, 'weight': 2.0, 'raw_analysis': 'kui+Adv', 'end': 10}, 
       {'start': 7, 'weight': 200.0, 'raw_analysis': 'kui+Guess+N+Sg+Nom', 'end': 10}, 
       {'start': 7, 'weight': 201.0, 'raw_analysis': 'kui+Guess+N+Sg+Gen', 'end': 10}], 
      [{'start': 11, 'weight': 7.0, 'raw_analysis': 'jube+A+Sg+Nom', 'end': 21}, 
       {'start': 11, 'weight': 7.0, 'raw_analysis': 'jube+Adv', 'end': 21}], 
      [{'start': 22, 'weight': 0.0, 'raw_analysis': '...+CLB', 'end': 25}]
    ]
    assert results == expected_results
    
    # Case 2: word normalizations with unknown words
    text = Text('''päris hää !''')
    text.tag_layer(['compound_tokens', 'words'])
    # Add multiple normalized forms (include unknown words)
    for word in text.words:
        if word.text == 'hää':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['hea', 'hääx0R', 'head']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='hea') )
                word.add_annotation( Annotation(word, normalized_form='hääx0R') )
                word.add_annotation( Annotation(word, normalized_form='head') )
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = \
    [
        [{'weight': 5.0, 'end': 5, 'raw_analysis': 'päris+A', 'start': 0}, 
         {'weight': 5.0, 'end': 5, 'raw_analysis': 'päris+Adv', 'start': 0}, 
         {'weight': 7.0, 'end': 5, 'raw_analysis': 'pärima+V+Pers+Prt+Ind+Sg3+Aff', 'start': 0}], 
        [{'weight': 4.0, 'end': 9, 'raw_analysis': 'hea+A+Sg+Nom', 'start': 6}, 
         {'weight': 4.0, 'end': 9, 'raw_analysis': 'hea+N+Sg+Nom', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+A+Sg+Gen', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+N+Sg+Gen', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+A+Pl+Nom', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+N+Pl+Nom', 'start': 6}, 
         {'weight': 6.0, 'end': 9, 'raw_analysis': 'hea+A+Sg+Par', 'start': 6}, 
         {'weight': 6.0, 'end': 9, 'raw_analysis': 'hea+N+Sg+Par', 'start': 6}], 
        [{'weight': 0.0, 'end': 11, 'raw_analysis': '!+CLB', 'start': 10}] ]
    assert results == expected_results


@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_split_analyses_into_morphemes():
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import split_into_morphemes
    
    test_data = [ {'word':'talv',\
                   'raw_analysis':'talv+N+Sg+Nom', \
                   'expected_morphemes':['talv+N+Sg+Nom']}, \
                  {'word':'millegis',\
                   'raw_analysis':'miski+Pron+Sg+Ine+Use/NotNorm', \
                   'expected_morphemes':['miski+Pron+Sg+Ine', '+Use/NotNorm']}, \
                  {'word':'öelnud',\
                   'raw_analysis':'ütlema+V+Pers+Prt+Ind+Neg', \
                   'expected_morphemes':['ütlema+V+Pers+Prt+Ind+Neg']}, \
                  {'word':'karutapjagi',\
                   'raw_analysis':'karu+N+Sg+Gen#tapma+V+Der/ja+N+Sg+Nom+Foc/gi' , \
                   'expected_morphemes':['karu+N+Sg+Gen', 'tapma+V+Der', 'ja+N+Sg+Nom', '+Foc/gi']}, \
                  {'word':'ülipüüdlik',\
                   'raw_analysis':'üli+Pref#püüd+N+Der/lik+A+Sg+Nom' , \
                   'expected_morphemes':['üli+Pref', 'püüd+N+Der', 'lik+A+Sg+Nom']}, \
                  {'word':'laupäevahommikuti',\
                   'raw_analysis':'laupäev+N+Sg+Gen#hommik+N+Der/ti+Adv' , \
                   'expected_morphemes':['laupäev+N+Sg+Gen', 'hommik+N+Der', 'ti+Adv']}, \
                  {'word':'killuke',\
                   'raw_analysis':'kild+N+Dim/ke+Sg+Nom' , \
                   'expected_morphemes':['kild+N+Dim', 'ke+Sg+Nom']}, \
                  {'word':'iluaedasid',\
                   'raw_analysis':'ilu+N+Sg+Gen#aed+N+Pl+Par+Use/Rare' , \
                   'expected_morphemes':['ilu+N+Sg+Gen', 'aed+N+Pl+Par', '+Use/Rare']}, \
                  {'word':'kohtumispaik',\
                   'raw_analysis':'kohtumine+N+Der/minus#paik+N+Sg+Nom' , \
                   'expected_morphemes':['kohtumine+N+Der/minus', 'paik+N+Sg+Nom']}, \
                  {'word':'lahkumisvalust',\
                   'raw_analysis':'lahkuma+V+Der/mine+N+Der/minus#valu+N+Sg+Ela' , \
                   'expected_morphemes':['lahkuma+V+Der', 'mine+N+Der/minus', 'valu+N+Sg+Ela']}, \
                  {'word':'hingamisteed',\
                   'raw_analysis':'hingamine+N+Der/minus#tee+N+Pl+Nom' , \
                   'expected_morphemes':['hingamine+N+Der/minus', 'tee+N+Pl+Nom']}, \
                  {'word':'arvamis-',\
                   'raw_analysis':'arvama+V+Der/mine+N+Der/minus' , \
                   'expected_morphemes':['arvama+V+Der', 'mine+N+Der/minus']}, \
                ]
    for test_item in test_data:
        input_raw_analysis = test_item['raw_analysis']
        morphemes = split_into_morphemes( input_raw_analysis )
        assert  morphemes == test_item['expected_morphemes']


@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_extract_morpheme_features():
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import split_into_morphemes, extract_morpheme_features
    from collections import OrderedDict
    
    test_data = [ {'word':'talv',\
                   'raw_analysis':'talv+N+Sg+Nom', \
                   'expected_features': OrderedDict([('morphemes', ['talv']), ('postags', ['N']), ('forms', ['Sg+Nom']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  {'word':'millegis',\
                   'raw_analysis':'miski+Pron+Sg+Ine+Use/NotNorm', \
                   'expected_features': OrderedDict([('morphemes', ['miski']), ('postags', ['Pron']), ('forms', ['Sg+Ine']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', ['Use/NotNorm'])])}, \
                  {'word':'öelnud',\
                   'raw_analysis':'ütlema+V+Pers+Prt+Ind+Neg', \
                   'expected_features': OrderedDict([('morphemes', ['ütlema']), ('postags', ['V']), ('forms', ['Pers+Prt+Ind+Neg']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])])}, \
                  {'word':'karutapjagi',\
                   'raw_analysis':'karu+N+Sg+Gen#tapma+V+Der/ja+N+Sg+Nom+Foc/gi' , \
                   'expected_features': OrderedDict([('morphemes', ['karu', 'tapma', 'ja']), ('postags', ['N', 'V', 'N']), \
                                                     ('forms', ['Sg+Gen', 'Der', 'Sg+Nom']), ('has_clitic', [False,False,True]), \
                                                     ('is_guessed', [False,False,False]), ('usage', ['','',''])])}, \
                  {'word':'ülipüüdlik',\
                   'raw_analysis':'üli+Pref#püüd+N+Der/lik+A+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['üli', 'püüd', 'lik']), ('postags', ['Pref', 'N', 'A']), \
                                                     ('forms', ['', 'Der', 'Sg+Nom']), ('has_clitic', [False,False,False]), \
                                                     ('is_guessed', [False,False,False]), ('usage', ['','',''])])}, \
                  {'word':'laupäevahommikuti',\
                   'raw_analysis':'laupäev+N+Sg+Gen#hommik+N+Der/ti+Adv' , \
                   'expected_features': OrderedDict([('morphemes', ['laupäev', 'hommik', 'ti']), ('postags', ['N', 'N', 'Adv']), \
                                                     ('forms', ['Sg+Gen', 'Der', '']), ('has_clitic', [False,False,False]), \
                                                     ('is_guessed', [False,False,False]), ('usage', ['','',''])])}, \
                  {'word':'killuke',\
                   'raw_analysis':'kild+N+Dim/ke+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['kild', 'ke']), ('postags', ['N', '']), ('forms', ['Dim', 'Sg+Nom']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  {'word':'iluaedasid',\
                   'raw_analysis':'ilu+N+Sg+Gen#aed+N+Pl+Par+Use/Rare' , \
                   'expected_features': OrderedDict([('morphemes', ['ilu', 'aed']), ('postags', ['N', 'N']), ('forms', ['Sg+Gen', 'Pl+Par']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['','Use/Rare'])])}, \
                  {'word':'vannaema',\
                   'raw_analysis':'vanna+Guess#ema+N+Sg+Gen' , \
                   'expected_features': OrderedDict([('morphemes', ['vanna', 'ema']), ('postags', ['', 'N']), ('forms', ['', 'Sg+Gen']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [True,False]), ('usage', ['',''])])}, \
                  # It should also work on empty string
                  {'word':'',\
                   'raw_analysis':'' , \
                   'expected_features': OrderedDict([('morphemes', []), ('postags', []), ('forms', []), ('has_clitic', []), \
                                                     ('is_guessed', []), ('usage', [])])}, \
                  # Words containing shortenings
                  {'word':'arvamis-',\
                   'raw_analysis':'arvama+V+Der/mine+N+Der/minus' , \
                   'expected_features': OrderedDict([('morphemes', ['arvama', 'mine']), ('postags', ['V', 'N']), ('forms', ['Der', 'Der/minus']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  {'word':'kohtumispaik',\
                   'raw_analysis':'kohtumine+N+Der/minus#paik+N+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['kohtumine', 'paik']), ('postags', ['N', 'N']), ('forms', ['Der/minus', 'Sg+Nom']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  {'word':'hingamisteed',\
                   'raw_analysis':'hingamine+N+Der/minus#tee+N+Pl+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['hingamine', 'tee']), ('postags', ['N', 'N']), ('forms', ['Der/minus', 'Pl+Nom']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  # Guessed proper nouns
                  {'word':'Sallamaa',\
                   'raw_analysis':'Sallamaa+Guess+N+Prop+Sg+Gen' , \
                   'expected_features': OrderedDict([('morphemes', ['Sallamaa']), ('postags', ['N+Prop']), ('forms', ['Sg+Gen']), \
                                                     ('has_clitic', [False]), ('is_guessed', [True]), ('usage', [''])])}, \
                  {'word':'Inglismaal',\
                   'raw_analysis':'Inglismaa+Guess+N+Prop+Sg+Ade' , \
                   'expected_features': OrderedDict([('morphemes', ['Inglismaa']), ('postags', ['N+Prop']), ('forms', ['Sg+Ade']), \
                                                     ('has_clitic', [False]), ('is_guessed', [True]), ('usage', [''])])}, \
                  # Punctuation
                  {'word':'--',\
                   'raw_analysis':'--+PUNCT' , \
                   'expected_features': OrderedDict([('morphemes', ['--']), ('postags', ['PUNCT']), ('forms', ['']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  {'word':'"',\
                   'raw_analysis':'"+PUNCT' , \
                   'expected_features': OrderedDict([('morphemes', ['"']), ('postags', ['PUNCT']), ('forms', ['']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  {'word':')',\
                   'raw_analysis':')+PUNCT+RIGHT' , \
                   'expected_features': OrderedDict([('morphemes', [')']), ('postags', ['PUNCT']), ('forms', ['RIGHT']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  # Abbreviations
                  {'word':'vrd',\
                   'raw_analysis':'vrd+ABBR' , \
                   'expected_features': OrderedDict([('morphemes', ['vrd']), ('postags', ['ABBR']), ('forms', ['']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                ]
    for test_item in test_data:
        input_raw_analysis = test_item['raw_analysis']
        morphemes = split_into_morphemes( input_raw_analysis )
        morpheme_feats = extract_morpheme_features( morphemes )
        #print(morpheme_feats)
        assert morpheme_feats == test_item['expected_features']



@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_morphemes_lemmas_output():
    from estnltk import Text
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import HfstEstMorphAnalyser
    
    # Test HfstEstMorphAnalyser's morphemes_lemmas output format
    hfstAnalyser = HfstEstMorphAnalyser( output_format='morphemes_lemmas' )

    # Case 1
    input_text_str = 'Ülipüüdlik vannaemake rohib võib-olla Zathumaeres iluaedasid.'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = [
       [{'weight': 54.0, 'end': 10, 'forms': ('', 'Sg+Nom'), 'postags': ('Pref', 'A'), 'morphemes_lemmas': ('üli', 'püüdlik'), 'is_guessed': False, 'has_clitic': False, 'start': 0, 'usage': ()}, 
        {'weight': 64.0, 'end': 10, 'forms': ('', 'Der', 'Sg+Nom'), 'postags': ('Pref', 'N', 'A'), 'morphemes_lemmas': ('üli', 'püüd', 'lik'), 'is_guessed': False, 'has_clitic': False, 'start': 0, 'usage': ()},
        {'weight': 249.0, 'end': 10, 'forms': ('', 'Der', 'Sg+Nom'), 'postags': ('', 'N', 'A'), 'morphemes_lemmas': ('üli', 'püüd', 'lik'), 'is_guessed': True, 'has_clitic': False, 'start': 0, 'usage': ()}], 
       [{'weight': 239.0, 'end': 21, 'forms': ('', 'Sg+Nom'), 'postags':  ('', 'N'), 'morphemes_lemmas': ('vanna', 'emake'), 'is_guessed': True, 'has_clitic': False, 'start': 11, 'usage': ()}], 
       [{'weight': 10.0, 'end': 27, 'forms': ('Pers+Prs+Ind+Sg3+Aff',), 'postags': ('V',), 'morphemes_lemmas': ('rohima',), 'is_guessed': False, 'has_clitic': False, 'start': 22, 'usage': ()}], 
       [{'weight': 5.0, 'end': 37, 'forms': ('',), 'postags': ('Adv',), 'morphemes_lemmas': ('võib-olla',), 'is_guessed': False, 'has_clitic': False, 'start': 28, 'usage': ()}], 
       [{'weight': float('inf'), 'end': 49, 'forms': None, 'postags': None, 'morphemes_lemmas': None, 'is_guessed': None, 'has_clitic': None, 'start': 38, 'usage': None}], 
       [{'weight': 74.0, 'end': 60, 'forms': ('Pl+Par',), 'postags': ('N',), 'morphemes_lemmas': ('iluaed',), 'is_guessed': False, 'has_clitic': False, 'start': 50, 'usage': ('Use/Rare',)}, 
        {'weight': 87.0, 'end': 60, 'forms': ('Sg+Gen', 'Pl+Par'), 'postags': ('N', 'N'), 'morphemes_lemmas': ('ilu', 'aed'), 'is_guessed': False, 'has_clitic': False, 'start': 50, 'usage': ('Use/Rare',)} ], 
       [{'weight': 0.0, 'end': 61, 'forms': ('',), 'postags': ('CLB',), 'morphemes_lemmas': ('.',), 'is_guessed': False, 'has_clitic': False, 'start': 60, 'usage': ()}]
    ]
    assert results == expected_results
    
    # Case 2
    input_text_str = 'Äralõigatud ühendusega allmaaraudteejaamaski ulgus tuulekene.'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = [
       [{'postags': ('Adv', 'V', 'A'), 'is_guessed': False, 'end': 11, 'morphemes_lemmas': ('ära', 'lõikama', 'tud'), 'has_clitic': False, 'forms': ('', 'Der', ''), 'weight': 60.0, 'start': 0, 'usage': ()}, 
        {'postags': ('Adv', 'V', 'A'), 'is_guessed': False, 'end': 11, 'morphemes_lemmas': ('ära', 'lõikama', 'tu'), 'has_clitic': False, 'forms': ('', 'Der', 'Pl+Nom'), 'weight': 61.0, 'start': 0, 'usage': ()}], 
       [{'postags': ('N',), 'is_guessed': False, 'end': 22, 'morphemes_lemmas': ('ühendus',), 'has_clitic': False, 'forms': ('Sg+Com',), 'weight': 9.0, 'start': 12, 'usage': ()}, 
        {'postags': ('V', 'N'), 'is_guessed': False, 'end': 22, 'morphemes_lemmas': ('ühendama', 'us'), 'has_clitic': False, 'forms': ('Der', 'Sg+Com'), 'weight': 19.0, 'start': 12, 'usage': ()}], 
       [{'postags': ('N', 'N'), 'is_guessed': False, 'end': 44, 'morphemes_lemmas': ('allmaaraudtee', 'jaam'), 'has_clitic': True, 'forms': ('Sg+Gen', 'Sg+Ine'), 'weight': 152.0, 'start': 23, 'usage': ()}, 
        {'postags': ('Pref', 'N', 'N'), 'is_guessed': False, 'end': 44, 'morphemes_lemmas': ('all', 'maa', 'raudteejaam'), 'has_clitic': True, 'forms': ('', 'Sg+Gen', 'Sg+Ine'), 'weight': 161.0, 'start': 23, 'usage': ()}, 
        {'postags': ('Pref', 'N', 'N', 'N'), 'is_guessed': False, 'end': 44, 'morphemes_lemmas': ('all', 'maa', 'raudtee', 'jaam'), 'has_clitic': True, 'forms': ('', 'Sg+Gen', 'Sg+Gen', 'Sg+Ine'), 'weight': 178.0, 'start': 23, 'usage': ()}], 
       [{'postags': ('V',), 'is_guessed': False, 'end': 50, 'morphemes_lemmas': ('ulguma',), 'has_clitic': False, 'forms': ('Pers+Prt+Ind+Sg3+Aff',), 'weight': 10.0, 'start': 45, 'usage': ()}], 
       [{'postags': ('N',), 'is_guessed': False, 'end': 60, 'morphemes_lemmas': ('tuuleke',), 'has_clitic': False, 'forms': ('Sg+Nom',), 'weight': 41.0, 'start': 51, 'usage': ('Use/Rare',)}, 
        {'postags': ('N', ''), 'is_guessed': False, 'end': 60, 'morphemes_lemmas': ('tuul', 'ke'), 'has_clitic': False, 'forms': ('Dim', 'Sg+Nom'), 'weight': 46.0, 'start': 51, 'usage': ('Use/Rare',)}],
       [{'postags': ('CLB',), 'is_guessed': False, 'end': 61, 'morphemes_lemmas': ('.',), 'has_clitic': False, 'forms': ('',), 'weight': 0.0, 'start': 60, 'usage': ()}]
    ]
    assert results == expected_results

    # *** Test lookup method
    
    # Case 3
    records = hfstAnalyser.lookup('alpikannike')
    #print(records)
    expected_records = [ \
        {'has_clitic': False, 'morphemes_lemmas': ('alpikann', 'ke'), 'forms': ('Dim', 'Sg+Nom'), 'weight': 51.0, 'postags': ('N', ''), 'usage': (), 'is_guessed': False}, \
        {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kannike'), 'forms': ('', 'Sg+Nom'), 'weight': 56.0, 'postags': ('Pref', 'N'), 'usage': (), 'is_guessed': False}, \
        {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kann', 'ke'), 'forms': ('', 'Dim', 'Sg+Nom'), 'weight': 63.0, 'postags': ('Pref', 'N', ''), 'usage': (), 'is_guessed': False}, \
        {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kann', 'ike'), 'forms': ('', 'Sg+Nom', 'Sg+Nom'), 'weight': 106.0, 'postags': ('Pref', 'N', 'N'), 'usage': (), 'is_guessed': False}, \
        {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kannike'), 'forms': ('', 'Sg+Nom'), 'weight': 241.0, 'postags': ('', 'N'), 'usage': (), 'is_guessed': True} \
    ]
    #{'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kannike'), 'forms': ('', 'Sg+Nom'), 'weight': 240.0, 'postags': ('', 'N'), 'usage': (), 'is_guessed': True}, \
    #{'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kann', 'ke'), 'forms': ('', 'Dim', 'Sg+Nom'), 'weight': 250.0, 'postags': ('', 'N', ''), 'usage': (), 'is_guessed': True} \
    assert records == expected_records
    
    # Case 4
    records = hfstAnalyser.lookup('üleguugeldanud') # as in: "Oled ennast täitsa üleguugeldanud!"
    #print(records)
    expected_records = [ \
        {'weight': 64.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'A'), 'forms': ('', 'Der', ''), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nud'), 'has_clitic': False}, \
        {'weight': 64.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'A'), 'forms': ('', 'Der', 'Sg+Nom'), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nud'), 'has_clitic': False}, \
        {'weight': 65.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'A'), 'forms': ('', 'Der', 'Pl+Nom'), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nud'), 'has_clitic': False}, \
        {'weight': 65.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'N'), 'forms': ('', 'Der', 'Pl+Nom'), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nu'), 'has_clitic': False} \
    ]
    assert records == expected_records



@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_with_guessing_switched_on_and_off():
    from estnltk import Text
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import HfstEstMorphAnalyser
    
    # Test HfstEstMorphAnalyser's with guessing switched on and off
    # Case 1: lookup
    hfstAnalyser = HfstEstMorphAnalyser( output_format='raw', remove_guesses=True )
    hfstAnalyserGuesser = HfstEstMorphAnalyser( output_format='raw' )
    records1 = hfstAnalyser.lookup('kiwikübarad')
    assert records1 == []
    records2 = hfstAnalyserGuesser.lookup('kiwikübarad')
    assert records2 == [{'raw_analysis': 'kiwi+Guess#kübar+N+Pl+Nom', 'weight': 239.0}]
    
    # Case 2: tagging
    text = Text('bronzemehikesed')
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser = HfstEstMorphAnalyser(remove_guesses=True)
    hfstAnalyserGuesser = HfstEstMorphAnalyser(output_layer='hfst_gt_morph_analysis_w_guesses')
    hfstAnalyser.tag(text)
    results1 = text['hfst_gt_morph_analysis'].to_records()
    assert results1 == [[{'weight': float('inf'), 'postags': None, 'forms': None, 'morphemes_lemmas': None, 'end': 15, 'usage': None, 'start': 0, 'has_clitic': None, 'is_guessed': None}]]
    hfstAnalyserGuesser.tag(text)
    results2 = text['hfst_gt_morph_analysis_w_guesses'].to_records()
    assert results2 == [[{'weight': 240.0, 'postags': ('', 'N'), 'forms': ('', 'Pl+Nom'), 'morphemes_lemmas': ('bronze', 'mehike'), 'end': 15, 'usage': (), 'start': 0, 'has_clitic': False, 'is_guessed': True}, \
                         {'weight': 242.0, 'postags': ('', 'N'), 'forms': ('', 'Pl+Nom'), 'morphemes_lemmas': ('bronze', 'mehikene'), 'end': 15, 'usage': (), 'start': 0, 'has_clitic': False, 'is_guessed': True}]] 

