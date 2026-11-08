# Đáp án vấn đáp nghiệp vụ

**1. FIFO và AVCO khác nhau thế nào, ảnh hưởng gì đến giá vốn?**
FIFO (nhập trước xuất trước): giá vốn xuất kho lấy theo giá của lô nhập sớm nhất còn trong kho; tồn cuối kỳ phản ánh giá lô mới nhất. AVCO (bình quân gia quyền di động): mỗi lần nhập, giá vốn bình quân = (giá trị tồn cũ + giá trị nhập) / (số lượng tồn cũ + số lượng nhập), giá xuất dùng giá bình quân hiện tại. Khi giá mua biến động, FIFO làm giá vốn bám sát giá cũ (lãi gộp biến động theo giá mới), AVCO làm mượt giá vốn. Ví dụ: nhập 10 cái @100 rồi 10 cái @120, xuất 10: FIFO = 1.000; AVCO = 1.100.

**2. Khi nào dùng Lot, khi nào dùng Serial?**
Serial: mỗi đơn vị có một số định danh duy nhất (laptop, máy in) → truy xuất, bảo hành từng chiếc; số lượng mỗi serial = 1. Lot: một nhóm sản phẩm cùng sản xuất/nhập một đợt (giấy, thực phẩm, thuốc) → quản lý hạn dùng, thu hồi theo lô; một lot có nhiều số lượng.

**3. Kiểm soát hóa đơn theo số lượng đặt và số lượng nhận/giao khác nhau ra sao?**
Theo số lượng đặt/Ordered: được lập hóa đơn ngay khi xác nhận đơn, không cần nhận/giao hàng (hợp cho dịch vụ, trả trước). Theo số lượng nhận/giao (Received/Delivered): chỉ lập hóa đơn cho phần đã thực nhận/thực giao; chưa nhận thì "no invoiceable line". Đây là đối chiếu 3 bên (PO – phiếu nhận – hóa đơn) giúp tránh thanh toán cho hàng chưa về; với bán hàng, giao thiếu thì chỉ xuất hóa đơn phần đã giao.

**4. Route MTO và MTS là gì?**
MTS (Make To Stock): bán/xuất từ tồn kho có sẵn; hàng thiếu được bổ sung bằng quy tắc Min/Max (Replenishment). MTO (Make To Order): mỗi đơn bán tự sinh nhu cầu mua/sản xuất riêng cho đúng số lượng đơn, hàng về rồi giao khách (không giữ tồn). Dropship: NCC giao thẳng cho khách, không qua kho.

**5. Vì sao tồn On Hand khác Forecasted?**
On Hand = số lượng thực tế đang nằm trong kho (quant). Forecasted = On Hand + hàng sắp về (PO/phiếu nhập chưa Done) − hàng đã cam kết xuất (SO/phiếu xuất chưa Done) (± sản xuất). Vì thế sau khi xác nhận SO hoặc PO nhưng chưa validate phiếu kho, hai số này lệch nhau.
