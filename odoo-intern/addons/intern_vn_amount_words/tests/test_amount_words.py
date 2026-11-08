from odoo.tests import TransactionCase, tagged

from ..models.amount_words import amount_to_words_vn


@tagged('post_install', '-at_install')
class TestAmountWords(TransactionCase):

    def test_cases(self):
        cases = {
            0: "Không đồng chẵn.",
            5: "Năm đồng chẵn.",
            10: "Mười đồng chẵn.",
            11: "Mười một đồng chẵn.",
            15: "Mười lăm đồng chẵn.",
            21: "Hai mươi mốt đồng chẵn.",
            105: "Một trăm lẻ năm đồng chẵn.",
            1000: "Một nghìn đồng chẵn.",
            1005: "Một nghìn không trăm lẻ năm đồng chẵn.",
            15320500: "Mười lăm triệu ba trăm hai mươi nghìn năm trăm đồng chẵn.",
            1000000000: "Một tỷ đồng chẵn.",
            1001000: "Một triệu không trăm lẻ một nghìn đồng chẵn.",
        }
        for number, expected in cases.items():
            self.assertEqual(amount_to_words_vn(number), expected, number)

    def test_model_wrapper(self):
        words = self.env['vn.amount.words'].amount_to_words(2500000)
        self.assertEqual(words, "Hai triệu năm trăm nghìn đồng chẵn.")
