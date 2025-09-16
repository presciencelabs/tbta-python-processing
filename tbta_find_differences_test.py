import unittest
from tbta_find_differences import find_differences, DiffData


class TestDiffAnalysis(unittest.TestCase):

    def test_Matt_2_8(self):
        old = 'Wan Hirudis mautus urang-urang nang bailmu tu ka Betlehem. “Tulakan ha bubuhan ikam wan bujur-bujur cari\'i anak <<nang cagar manjadi raja urang-urang Ibrani>>. Imbah bubuhan ikam manamuakan anak nang itu, hanyar langsung datangi aku. Wan padahakan ha bubuhan ikam lawan aku manganai daerah dimana anak nang itu baada sakira aku kawa tulak ka situ jua handak manyambah inya,” ujar Hirudis baucap lawan urang-urang nang bailmu tu.'
        new = 'Imbah itu Hirudis manyuruh urang-urang nang bisa tu ka Betlehem. “Tulak ha bubuhan ikam wan cari bujur-bujur anak nang itu<<nang cagar jadi raja urang Ibrani>>. Imbah bubuhan ikam tatamu anak nang itu, langsung datangi aku. Padahakan ha bubuhan ikam lawan aku, di dairah mana anak nang itu baada, sakira aku kawa tulak ka situ jua handak manyambah inya,” ujar Hirudis baucap lawan urang-urang nang bisa tu.'
        expected = [
            DiffData('Wan->Imbah itu', (0, 3), (0, 9)),
            DiffData('mautus->manyuruh', (12, 18), (18, 26)),
            DiffData('bailmu->bisa', (36, 42), (44, 48)),
            DiffData('Tulakan->Tulak', (60, 67), (66, 71)),
            DiffData('->cari', (88, 88), (92, 97)),
            DiffData("cari'i->", (100, 107), (109, 109)),
            DiffData('->nang itu', (112, 112), (114, 122)),
            DiffData('manjadi->jadi', (125, 132), (135, 139)),
            DiffData('urang-urang->urang', (138, 149), (145, 150)),
            DiffData('manamuakan->tatamu', (179, 189), (180, 186)),
            DiffData('hanyar->', (205, 212), (202, 202)),
            DiffData('Wan->', (234, 238), (224, 224)),
            DiffData('padahakan->Padahakan', (238, 247), (224, 233)),
            DiffData('->,', (273, 273), (259, 260)),
            DiffData('manganai->di', (274, 282), (261, 263)),
            DiffData('daerah->dairah', (283, 289), (264, 270)),
            DiffData('dimana->mana', (290, 296), (271, 275)),
            DiffData('->,', (316, 316), (295, 296)),
            DiffData('bailmu->bisa', (418, 424), (398, 402)),
        ]
        actual = find_differences(old, new, try_match_words=True, separate_punctuation=True)
        self.assertListEqual(actual, expected)

    def test_Matt_2_9(self):
        old = 'Imbah urang-urang nang bailmu tu mandangar hal-hal nang diucapakan ulih Raja Hirudis, hanyar bubuhannya tarus tulakan. Bintang nang dilihat ulih urang-urang nang bailmu tu di dairah timur mandahului bubuhannya sampai bintang nang itu hanyar bamandak atas daerah dimana anak nang itu baada di Betlehem.'
        new = 'Imbah urang-urang nang bisa tu mandangar sual nang diucapakan ulih Raja Hirudis, lalu bubuhannya tulakan. Bintang nang dilihat ulih bubuhan nang bisa tu andakannya ada di dairah timur mandahului bubuhannya, sampai bintang nang itu bamandak di atas dairah wadah anak tu di Betlehem.'
        expected_simple = [
            DiffData('bailmu->bisa', (23, 29), (23, 27)),
            DiffData('hal-hal->sual', (43, 50), (41, 45)),
            DiffData('hanyar->lalu', (86, 92), (81, 85)),
            DiffData('tarus->', (103, 109), (96, 96)),
            DiffData('urang-urang->bubuhan', (145, 156), (132, 139)),
            DiffData('bailmu->bisa', (162, 168), (145, 149)),
            DiffData('->andakannya ada', (172, 172), (153, 168)),
            DiffData('->,', (209, 209), (205, 206)),
            DiffData('hanyar->', (234, 241), (231, 231)),
            DiffData('->di', (250, 250), (240, 243)),
            DiffData('daerah dimana->dairah wadah', (255, 268), (248, 260)),
            DiffData('nang itu baada->tu', (274, 288), (266, 268)),
        ]
        expected_full = [
            DiffData('bailmu->bisa', (23, 29), (23, 27)),
            DiffData('hal-hal->sual', (43, 50), (41, 45)),
            DiffData('hanyar->lalu', (86, 92), (81, 85)),
            DiffData('tarus->', (103, 109), (96, 96)),
            DiffData('urang-urang->bubuhan', (145, 156), (132, 139)),
            DiffData('bailmu->bisa', (162, 168), (145, 149)),
            DiffData('->andakannya ada', (172, 172), (153, 168)),
            DiffData('->,', (209, 209), (205, 206)),
            DiffData('hanyar->', (234, 241), (231, 231)),
            DiffData('->di', (250, 250), (240, 243)),
            DiffData('daerah->dairah', (255, 261), (248, 254)),
            DiffData('dimana->wadah', (262, 268), (255, 260)),
            DiffData('nang->', (274, 279), (266, 266)),
            DiffData('itu->tu', (279, 282), (266, 268)),
            DiffData('baada->', (282, 288), (268, 268)),
        ]
        actual_simple = find_differences(old, new)
        actual_full = find_differences(old, new, try_match_words=True, separate_punctuation=True)
        self.assertListEqual(actual_simple, expected_simple)
        self.assertListEqual(actual_full, expected_full)

    def test_Matt_4_24(self):
        old = 'Manusia mandangar manganai Nabi Isa di samuaan <<dairah>> Siria lalu dibawa sabarataan urang nang bapanyakitan, sabarataan urang nang banyak kasakitan, sabarataan urang nang disarungi ulih ruh-ruh jahat, sabarataan urang nang kejang-kejang, wan sabarataan urang nang lumpuh ulih bubuhannya ka wadah-Nya. Lalu Nabi Isa mawarasakan urang-urang nang itu.'
        new = 'Urang-urang nang mandangar sual Nabi Isa di saluruh <<dairah>> Siria lalu mambawa sabarataan urang nang bapanyakitan, urang nang disiksa sakit, urang nang kasarungan ruh-ruh jahat, urang nang gila babi, wan urang nang lumpuh ka Inya. Nabi Isa mawagasakan samunyaan urang tu.'
        expected = [
            DiffData('Manusia->Urang-urang nang', (0, 7), (0, 16)),
            DiffData('manganai->sual', (18, 26), (27, 31)),
            DiffData('samuaan->saluruh', (39, 46), (44, 51)),
            DiffData('dibawa->mambawa', (69, 75), (74, 81)),
            DiffData('sabarataan->', (112, 123), (118, 118)),
            DiffData('banyak kasakitan->disiksa sakit', (134, 150), (129, 142)),
            DiffData('sabarataan->', (152, 163), (144, 144)),
            DiffData('disarungi ulih->kasarungan', (174, 188), (155, 165)),
            DiffData('sabarataan->', (204, 215), (181, 181)),
            DiffData('kejang-kejang->gila babi', (226, 239), (192, 201)),
            DiffData('sabarataan->', (245, 256), (207, 207)),
            DiffData('ulih bubuhannya->', (274, 290), (225, 225)),
            DiffData('wadah-Nya->Inya', (293, 302), (228, 232)),
            DiffData('Lalu->', (304, 309), (234, 234)),
            DiffData('urang-urang nang->samunyaan urang', (330, 346), (255, 270)),
            DiffData('mawarasakan->mawagasakan', (318, 329), (243, 254)),
            DiffData('itu->tu', (347, 350), (271, 273)),
        ]
        actual = find_differences(old, new, try_match_words=True, separate_punctuation=True)
        self.assertListEqual(actual, expected)

    def test_Matt_9_28(self):
        old = 'Imbah Nabi Isa masuk ka rumah <<nang ditinggal-Nya di Kapernaum>>, urang-urang nang buta mandatangi Sidin. “Bujuranlah buhan ikam parcaya amun Aku bisa mawarasakan buhan ikam?” ujar Nabi Isa batakun lawan urang-urang nitu. “Tuan, inggih,” ujar urang-urang manyahuti.'
        new = 'Imbah Nabi Isa masuk ka rumah << wadah Sidin tinggal di Kapernaum>>, kadua urang picak nitu mandatangi Sidin. “Parcayalah bubuhan ikam amun Aku kawa mawagasakan bubuhan ikam?” ujar Nabi Isa batakun lawan bubuhannya. “Inggih Tuhan,” ujar bubuhannya manyahuti.'
        actual = find_differences(old, new, try_match_words=True, separate_punctuation=True)
        # This verse at one point caused an error due to an index issue
        self.assertIsNotNone(actual)

    def test_empty_new(self):
        old = "“Banyu di bawah langit Kukumpullah. Wan tanah nang karing mancungullah.” maka Allah maulah tanah nang karing mancungul."
        new = ''
        expected = [
            DiffData('"Banyu di bawah langit Kukumpullah. Wan tanah nang karing mancungullah." maka Allah maulah tanah nang karing mancungul.->', (0, 119), (0, 0)),
        ]
        actual = find_differences(old, new, try_match_words=True, separate_punctuation=True)
        self.assertListEqual(actual, expected)

    def test_empty_old(self):
        old = ''
        new = "“Banyu di bawah langit Kukumpullah. Wan tanah nang karing mancungullah.” maka Allah maulah tanah nang karing mancungul."
        expected = [
            DiffData('->"Banyu di bawah langit Kukumpullah. Wan tanah nang karing mancungullah." maka Allah maulah tanah nang karing mancungul.', (0, 0), (0, 119)),
        ]
        actual = find_differences(old, new, try_match_words=True, separate_punctuation=True)
        self.assertListEqual(actual, expected)

    def test_reversible_full(self):
        str1 = 'Bumi baluman bapotongan wan puang. Manukupi blah banyu nang dalam. Lalu Ruh Kudus Allah malayang-layang atas banyu.'
        str2 = 'Bumi baluman bapotongan wan puang. Kadap manukupi banyu nang dalam, lalu Ruh Kudus malayang-layang atas banyu.'
        expected_12_full = [
            DiffData('->Kadap', (35, 35), (35, 41)),
            DiffData('Manukupi->manukupi', (35, 43), (41, 49)),
            DiffData('blah->', (43, 48), (49, 49)), # the underlying diff is actually ' blah->'
            DiffData('.->,', (65, 66), (66, 67)),
            DiffData('Lalu->lalu', (67, 71), (68, 72)),
            DiffData('Allah->', (82, 88), (83, 83)),
        ]
        expected_21_full = [
            DiffData('Kadap->', (35, 41), (35, 35)),
            DiffData('manukupi->Manukupi', (41, 49), (35, 43)),
            DiffData('->blah', (49, 49), (43, 48)), # the underlying diff is actually '-> blah'
            DiffData(',->.', (66, 67), (65, 66)),
            DiffData('lalu->Lalu', (68, 72), (67, 71)),
            DiffData('->Allah', (83, 83), (82, 88)),
        ]
        actual_12_full = find_differences(str1, str2, try_match_words=True, separate_punctuation=True)
        actual_21_full = find_differences(str2, str1, try_match_words=True, separate_punctuation=True)
        self.assertListEqual(actual_12_full, expected_12_full)
        self.assertListEqual(actual_21_full, expected_21_full)

    def test_reversible_simple(self):
        str1 = 'Bumi baluman bapotongan wan puang. Manukupi blah banyu nang dalam. Lalu Ruh Kudus Allah malayang-layang atas banyu.'
        str2 = 'Bumi baluman bapotongan wan puang. Kadap manukupi banyu nang dalam, lalu Ruh Kudus malayang-layang atas banyu.'
        expected_12_simple = [
            DiffData('Manukupi blah->Kadap manukupi', (35, 48), (35, 49)),
            DiffData('. Lalu->, lalu', (65, 71), (66, 72)),
            DiffData('Allah->', (82, 88), (83, 83)),
        ]
        expected_21_simple = [
            DiffData('Kadap manukupi->Manukupi blah', (35, 49), (35, 48)),
            DiffData(', lalu->. Lalu', (66, 72), (65, 71)),
            DiffData('->Allah', (83, 83), (82, 88)),
        ]
        actual_12_simple = find_differences(str1, str2)
        actual_21_simple = find_differences(str2, str1)
        self.assertListEqual(actual_12_simple, expected_12_simple)
        self.assertListEqual(actual_21_simple, expected_21_simple)


    def test_additional_sentence(self):
        str1 = "This is a test sentence."
        str2 = "This was a testy sentence. Here was another!"
        expected_simple = [
            DiffData('is->was', (5, 7), (5, 8)),
            DiffData('test->testy', (10, 14), (11, 16)),
            DiffData('->Here was another!', (24, 24), (26, 44)),
        ]
        actual_simple = find_differences(str1, str2)
        self.assertListEqual(actual_simple, expected_simple)


    def test_same_sentence(self):
        str1 = "This was a testy sentence. Here was another!"
        str2 = "This was a testy sentence. Here was another!"
        expected_simple = []
        actual_simple = find_differences(str1, str2)
        self.assertListEqual(actual_simple, expected_simple)


if __name__ == '__main__':
    unittest.main()