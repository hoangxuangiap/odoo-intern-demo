from odoo import api, models

DIGITS = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
SCALES = ['', 'nghìn', 'triệu']  # sau triệu là "tỷ", rồi lặp lại: nghìn tỷ, triệu tỷ...


def _read_triple(n, has_higher):
    """Đọc 1 nhóm 3 chữ số (0-999). has_higher=True nếu phía trước còn nhóm lớn hơn khác 0
    (khi đó 5 -> "không trăm lẻ năm")."""
    hundreds, tens, units = n // 100, (n // 10) % 10, n % 10
    words = []
    if hundreds or has_higher:
        words.append(f"{DIGITS[hundreds]} trăm")
    if tens > 1:
        words.append(f"{DIGITS[tens]} mươi")
    elif tens == 1:
        words.append("mười")
    elif units and (hundreds or has_higher):
        words.append("lẻ")
    if units:
        if units == 1 and tens > 1:
            words.append("mốt")
        elif units == 5 and tens >= 1:
            words.append("lăm")
        else:
            words.append(DIGITS[units])
    return ' '.join(words)


def amount_to_words_vn(amount, unit='đồng', whole_suffix=' chẵn'):
    """15320500 -> 'Mười lăm triệu ba trăm hai mươi nghìn năm trăm đồng chẵn.'"""
    number = int(round(amount or 0))
    if number == 0:
        return f"Không {unit}{whole_suffix}."
    negative = number < 0
    number = abs(number)
    groups = []
    while number:
        groups.append(number % 1000)
        number //= 1000
    parts = []
    for idx in range(len(groups) - 1, -1, -1):
        group = groups[idx]
        if not group:
            continue
        has_higher = any(groups[idx + 1:])
        scale = (SCALES[idx % 3] + ' tỷ' * (idx // 3)).strip()
        parts.append(f"{_read_triple(group, has_higher)} {scale}".strip())
    sentence = ' '.join(parts)
    if negative:
        sentence = 'âm ' + sentence
    return f"{sentence[0].upper()}{sentence[1:]} {unit}{whole_suffix}."


class VnAmountWords(models.AbstractModel):
    """Bọc hàm trên thành model trừu tượng để QWeb gọi được:
    o.env['vn.amount.words'].amount_to_words(o.amount_total, o.currency_id)"""
    _name = 'vn.amount.words'
    _description = 'Vietnamese Amount in Words'

    @api.model
    def amount_to_words(self, amount, currency=None):
        if currency and currency.name != 'VND':
            return amount_to_words_vn(amount, unit=currency.name, whole_suffix='')
        return amount_to_words_vn(amount)
