import unittest
from tbta_find_differences import compare_text_words


class TestDiffAnalysis(unittest.TestCase):

    def test_Matt_2_8(self):
        old = 'Wan Hirudis mautus urang-urang nang bailmu tu ka Betlehem. “Tulakan ha bubuhan ikam wan bujur-bujur cari\'i anak <<nang cagar manjadi raja urang-urang Ibrani>>. Imbah bubuhan ikam manamuakan anak nang itu, hanyar langsung datangi aku. Wan padahakan ha bubuhan ikam lawan aku manganai daerah dimana anak nang itu baada sakira aku kawa tulak ka situ jua handak manyambah inya,” ujar Hirudis baucap lawan urang-urang nang bailmu tu.'
        new = 'Imbah itu Hirudis manyuruh urang-urang nang bisa tu ka Betlehem. “Tulak ha bubuhan ikam wan cari bujur-bujur anak nang itu<<nang cagar jadi raja urang Ibrani>>. Imbah bubuhan ikam tatamu anak nang itu, langsung datangi aku. Padahakan ha bubuhan ikam lawan aku, di dairah mana anak nang itu baada, sakira aku kawa tulak ka situ jua handak manyambah inya,” ujar Hirudis baucap lawan urang-urang nang bisa tu.'
        expected = {
            'Wan->Imbah itu': ['2:8,0-3,0-9'],
            'mautus->manyuruh': ['2:8,12-18,18-26'],
            'bailmu->bisa': ['2:8,36-42,44-48', '2:8,418-424,398-402'],
            'Tulakan->Tulak': ['2:8,60-67,66-71'],
            '->cari': ['2:8,88-88,92-97'],
            "cari'i->": ['2:8,100-107,109-109'],
            '<<->': ['2:8,111-114,113-114'],
            '->itu<<nang': ['2:8,119-119,119-129'],
            'manjadi->jadi': ['2:8,125-132,135-139'],
            'urang-urang->urang': ['2:8,138-149,145-150'],
            'manamuakan->tatamu': ['2:8,179-189,180-186'],
            'hanyar->': ['2:8,205-212,202-202'],
            'Wan->': ['2:8,234-238,224-224'],
            'padahakan->Padahakan': ['2:8,238-247,224-233'],
            '->,': ['2:8,273-273,259-261', '2:8,316-316,295-297'],
            'manganai->di': ['2:8,273-283,261-264'],
            'daerah->dairah': ['2:8,283-289,264-270'],
            'dimana->mana': ['2:8,290-296,271-275'],
        }
        actual = {}
        compare_text_words('2:8', old, new, actual)
        print(actual)
        self.assertDictEqual(actual, expected)

    def test_Matt_2_9(self):
        old = 'Imbah urang-urang nang bailmu tu mandangar hal-hal nang diucapakan ulih Raja Hirudis, hanyar bubuhannya tarus tulakan. Bintang nang dilihat ulih urang-urang nang bailmu tu di dairah timur mandahului bubuhannya sampai bintang nang itu hanyar bamandak atas daerah dimana anak nang itu baada di Betlehem.'
        new = 'Imbah urang-urang nang bisa tu mandangar sual nang diucapakan ulih Raja Hirudis, lalu bubuhannya tulakan. Bintang nang dilihat ulih bubuhan nang bisa tu andakannya ada di dairah timur mandahului bubuhannya, sampai bintang nang itu bamandak di atas dairah wadah anak tu di Betlehem.'
        expected = {
            'bailmu->bisa': ['2:9,23-29,23-27', '2:9,162-168,145-149'],
            'hal-hal->sual': ['2:9,43-50,41-45'],
            'hanyar->lalu': ['2:9,86-92,81-85'],
            'tarus->': ['2:9,103-109,96-96'],
            'urang-urang->bubuhan': ['2:9,145-156,132-139'],
            '->andakannya ada': ['2:9,172-172,153-168'],
            '->,': ['2:9,209-209,205-207'],
            'hanyar->': ['2:9,234-241,231-231'],
            '->di': ['2:9,250-250,240-243'],
            'daerah->dairah': ['2:9,255-261,248-254'],
            'dimana->wadah': ['2:9,261-268,254-260'],
            'nang->': ['2:9,274-279,266-266'],
            'itu->tu': ['2:9,279-282,266-268'],
            'baada->': ['2:9,282-288,268-268'],
        }
        actual = {}
        compare_text_words('2:9', old, new, actual)
        print(actual)
        self.assertDictEqual(actual, expected)

    def test_Matt_4_24(self):
        old = 'Manusia mandangar manganai Nabi Isa di samuaan <<dairah>> Siria lalu dibawa sabarataan urang nang bapanyakitan, sabarataan urang nang banyak kasakitan, sabarataan urang nang disarungi ulih ruh-ruh jahat, sabarataan urang nang kejang-kejang, wan sabarataan urang nang lumpuh ulih bubuhannya ka wadah-Nya. Lalu Nabi Isa mawarasakan urang-urang nang itu.'
        new = 'Urang-urang nang mandangar sual Nabi Isa di saluruh <<dairah>> Siria lalu mambawa sabarataan urang nang bapanyakitan, urang nang disiksa sakit, urang nang kasarungan ruh-ruh jahat, urang nang gila babi, wan urang nang lumpuh ka Inya. Nabi Isa mawagasakan samunyaan urang tu.'
        expected = {
            'Manusia->Urang-urang nang': ['4:24,0-7,0-16'],
            'manganai->sual': ['4:24,18-26,27-31'],
            'samuaan->saluruh': ['4:24,39-46,44-51'],
            'dibawa->mambawa': ['4:24,69-75,74-81'],
            'sabarataan->': ['4:24,112-123,118-118', '4:24,152-163,144-144', '4:24,204-215,181-181', '4:24,245-256,207-207'],
            'banyak kasakitan->disiksa sakit': ['4:24,134-150,129-142'],
            'disarungi ulih->kasarungan': ['4:24,174-188,155-165'],
            'kejang-kejang->gila babi': ['4:24,226-239,192-201'],
            'ulih bubuhannya->': ['4:24,274-290,225-225'],
            'wadah-Nya->Inya': ['4:24,293-302,228-232'],
            'Lalu->': ['4:24,304-309,234-234'],
            'urang-urang nang->samunyaan urang': ['4:24,329-347,254-271'],
            'mawarasakan->mawagasakan': ['4:24,318-329,243-254'],
            'itu->tu': ['4:24,347-350,271-273'],
        }
        actual = {}
        compare_text_words('4:24', old, new, actual)
        print(actual)
        self.assertDictEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()