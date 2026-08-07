#!/usr/bin/env node
/**
 * Sinh slide báo cáo cuối kỳ từ số liệu thật của đề tài.
 *   node scripts/build_slides_final.js
 * Đầu ra: reports/DL_final_report.pptx
 */
const path = require("path");
const fs = require("fs");
const pptxgen = require(process.env.PPTX_LIB || "pptxgenjs");

const REPO = path.resolve(__dirname, "..");
const FIG = path.join(REPO, "report-latex", "figures");
const OUT = path.join(REPO, "reports", "DL_final_report.pptx");
const img = (n) => path.join(FIG, n);

// ── Bảng màu theo chủ đề: đêm trên đường, vàng cảnh báo, đỏ biển cấm ──
const NAVY = "16233A";   // nền tối, chiếm ưu thế
const NAVY_2 = "22334F"; // thẻ trên nền tối
const AMBER = "F2B705";  // nhấn chính
const RED = "C1272D";    // cảnh báo / kết quả âm
const GREEN = "2E7D57";  // đạt
const INK = "1A1A1A";    // chữ trên nền sáng
const GREY = "5B6570";   // chữ phụ
const LIGHT = "FFFFFF";
const TINT = "F1F3F6";   // nền thẻ trên slide sáng

const H = "Calibri";     // tiêu đề — dấu tiếng Việt render chắc chắn đúng
const B = "Calibri";     // thân — sans, an toàn khi QA

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Huynh Phat Loi";
pres.title = "Phat hien bien bao giao thong bang YOLO";

let n = 0;
const num = () => String(++n).padStart(2, "0");

// ── Trợ giúp bố cục ──────────────────────────────────────────────────
function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  return s;
}
function lightSlide(title, kicker) {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  if (kicker) {
    s.addText(kicker.toUpperCase(), {
      x: 0.6, y: 0.32, w: 8, h: 0.28, fontFace: B, fontSize: 11,
      color: AMBER, bold: true, charSpacing: 2, margin: 0,
    });
  }
  s.addText(title, {
    x: 0.6, y: kicker ? 0.62 : 0.45, w: 11.2, h: 0.75,
    fontFace: H, fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText(num(), {
    x: 12.5, y: 6.85, w: 0.5, h: 0.3, fontFace: B, fontSize: 10,
    color: GREY, align: "right", margin: 0,
  });
  return s;
}
// Thẻ số liệu lớn
function stat(s, x, y, w, value, label, valColor) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h: 1.5, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT },
  });
  s.addText(value, {
    x, y: y + 0.18, w, h: 0.72, fontFace: H, fontSize: 34, bold: true,
    color: valColor || NAVY, align: "center", margin: 0,
  });
  s.addText(label, {
    x: x + 0.1, y: y + 0.92, w: w - 0.2, h: 0.45, fontFace: B, fontSize: 11.5,
    color: GREY, align: "center", margin: 0,
  });
}
// Dòng có số thứ tự trong vòng tròn hổ phách
function numbered(s, x, y, w, idx, head, body) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: 0.42, h: 0.42, fill: { color: AMBER }, line: { color: AMBER },
  });
  s.addText(String(idx), {
    x, y: y + 0.04, w: 0.42, h: 0.34, fontFace: B, fontSize: 14, bold: true,
    color: NAVY, align: "center", margin: 0,
  });
  s.addText(head, {
    x: x + 0.6, y: y - 0.02, w: w - 0.6, h: 0.34,
    fontFace: B, fontSize: 15, bold: true, color: NAVY, margin: 0,
  });
  if (body) {
    s.addText(body, {
      x: x + 0.6, y: y + 0.32, w: w - 0.6, h: 0.62,
      fontFace: B, fontSize: 12.5, color: GREY, margin: 0,
    });
  }
}
function bullets(s, x, y, w, h, items, size) {
  s.addText(
    items.map((t, i) => ({
      text: t, options: { bullet: true, breakLine: i !== items.length - 1 },
    })),
    { x, y, w, h, fontFace: B, fontSize: size || 14, color: INK,
      paraSpaceAfter: 8, margin: 0, valign: "top" }
  );
}
function tableOf(s, x, y, w, rows, colW, opts) {
  s.addTable(rows, {
    x, y, w, colW,
    border: { type: "solid", color: "DDE2E8", pt: 0.75 },
    fontFace: B, fontSize: (opts && opts.fs) || 12, color: INK,
    align: "center", valign: "middle", rowH: (opts && opts.rowH) || 0.34,
    margin: 4,
  });
}
const hdr = (t) => ({ text: t, options: { bold: true, color: LIGHT, fill: { color: NAVY }, fontSize: 11.5 } });

// ═══════════════════ 1 · BÌA ═══════════════════
{
  const s = darkSlide();
  s.addText("BÁO CÁO CUỐI KỲ · HỌC PHẦN HỌC SÂU", {
    x: 0.9, y: 1.5, w: 11, h: 0.3, fontFace: B, fontSize: 12,
    color: AMBER, bold: true, charSpacing: 2.5, margin: 0,
  });
  s.addText("Phát hiện biển báo giao thông bằng YOLO", {
    x: 0.9, y: 2.05, w: 11.5, h: 0.95,
    fontFace: H, fontSize: 40, bold: true, color: LIGHT, margin: 0,
  });
  s.addText("Nén mô hình với chưng cất tri thức và lượng tử hoá", {
    x: 0.9, y: 3.0, w: 11.5, h: 0.6,
    fontFace: H, fontSize: 25, color: AMBER, margin: 0,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.9, y: 4.15, w: 5.4, h: 0.9, fill: { color: NAVY_2 },
    rectRadius: 0.08, line: { color: NAVY_2 },
  });
  s.addText("mAP tổng che giấu chi phí thật của việc nén mô hình", {
    x: 1.1, y: 4.3, w: 5.0, h: 0.6, fontFace: B, fontSize: 13,
    italic: true, color: LIGHT, margin: 0,
  });
  s.addText("Huỳnh Phát Lợi  ·  KHMT836016\nKhoa Công nghệ Thông tin  ·  Khoá 36\nTháng 08 / 2026", {
    x: 7.2, y: 4.15, w: 5.2, h: 1.1, fontFace: B, fontSize: 13,
    color: "C7D0DC", lineSpacing: 20, margin: 0,
  });
  s.addNotes("Báo cáo cuối kỳ. Giữa kỳ đã làm phân tích dữ liệu và so sánh YOLO với DETR; phần này chuyển sang bài toán triển khai: nén mô hình.");
}

// ═══════════════════ 2 · TỪ GIỮA KỲ ĐẾN CUỐI KỲ ═══════════════════
{
  const s = lightSlide("Từ giữa kỳ đến cuối kỳ", "Bối cảnh");
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 1.75, w: 5.6, h: 3.6, fill: { color: TINT },
    rectRadius: 0.08, line: { color: TINT },
  });
  s.addText("GIAI ĐOẠN 1 · GIỮA KỲ", {
    x: 0.95, y: 2.0, w: 5, h: 0.3, fontFace: B, fontSize: 11,
    bold: true, color: GREY, charSpacing: 1.5, margin: 0,
  });
  s.addText("Hai họ kiến trúc", {
    x: 0.95, y: 2.32, w: 5, h: 0.4, fontFace: H, fontSize: 19, bold: true, color: NAVY, margin: 0,
  });
  bullets(s, 0.95, 2.85, 4.95, 2.3, [
    "Phân tích khám phá dữ liệu đầy đủ",
    "YOLOv8n đối đầu DETR-ResNet50",
    "DETR chỉ đạt mAP@0,5 = 0,122 sau 10 chu kỳ — chưa hội tụ",
    "Kết luận: tiếp tục so với DETR không còn giá trị thông tin — mã lưu ở mid-work/",
  ], 13);

  s.addShape(pres.ShapeType.roundRect, {
    x: 6.6, y: 1.75, w: 6.1, h: 3.6, fill: { color: NAVY },
    rectRadius: 0.08, line: { color: NAVY },
  });
  s.addText("GIAI ĐOẠN 2 · CUỐI KỲ", {
    x: 6.95, y: 2.0, w: 5.4, h: 0.3, fontFace: B, fontSize: 11,
    bold: true, color: AMBER, charSpacing: 1.5, margin: 0,
  });
  s.addText("Bài toán triển khai", {
    x: 6.95, y: 2.32, w: 5.4, h: 0.4, fontFace: H, fontSize: 19, bold: true, color: LIGHT, margin: 0,
  });
  s.addText(
    ["Câu hỏi mới: làm sao đưa mô hình xuống phần cứng hạn chế?",
     "Chưng cất tri thức: YOLO26s dạy YOLO26n",
     "Lượng tử hoá sau huấn luyện: FP32 → INT8",
     "Đánh giá bằng pycocotools, tách AP theo kích thước vật thể"]
      .map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i !== a.length - 1 } })),
    { x: 6.95, y: 2.85, w: 5.45, h: 2.3, fontFace: B, fontSize: 13,
      color: "DCE3EC", paraSpaceAfter: 8, margin: 0, valign: "top" }
  );
  s.addNotes("Nhấn mạnh: đây không phải bỏ dở DETR mà là chuyển trọng tâm có lý do. Giữa kỳ đã trả lời xong câu hỏi kiến trúc.");
}

// ═══════════════════ 3 · VẤN ĐỀ ═══════════════════
{
  const s = lightSlide("Đạt mAP cao mới là một nửa bài toán", "Vấn đề");
  s.addText("Máy tính gắn trên xe không có card đồ hoạ máy chủ. Nửa còn lại của bài toán là ràng buộc tài nguyên.", {
    x: 0.6, y: 1.62, w: 12.1, h: 0.4, fontFace: B, fontSize: 15, color: GREY, margin: 0,
  });
  numbered(s, 0.6, 2.35, 5.9, 1, "Ràng buộc kép", "Vừa phải nhẹ để chạy nhúng, vừa phải chính xác để không bỏ sót biển báo");
  numbered(s, 0.6, 3.55, 5.9, 2, "Vật thể nhỏ", "Biển ở xa chỉ vài chục điểm ảnh — nhưng lại quyết định thời gian phản ứng của xe");
  numbered(s, 6.9, 2.35, 5.8, 3, "mAP tổng dễ gây hiểu nhầm", "Lấy trung bình bất kể kích thước; suy giảm ở nhóm khó bị pha loãng");
  numbered(s, 6.9, 3.55, 5.8, 4, "Dữ liệu quy mô vừa", "6.012 hộp bao, tỉ số mất cân bằng lớp lên tới 35,77 lần");
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 4.95, w: 12.1, h: 0.85, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY },
  });
  s.addText("Cả hai kỹ thuật nén đều được quảng bá bằng những con số hấp dẫn — nhưng luôn ở dạng mAP tổng. Đó chính là điểm đề tài đặt nghi vấn.", {
    x: 0.95, y: 5.12, w: 11.5, h: 0.55, fontFace: B, fontSize: 14, color: LIGHT, italic: true, margin: 0,
  });
}

// ═══════════════════ 4 · CÂU HỎI NGHIÊN CỨU ═══════════════════
{
  const s = lightSlide("Ba câu hỏi nghiên cứu", "Mục tiêu");
  const qs = [
    ["Chưng cất tri thức có thực sự giúp mô hình nhỏ tốt hơn?",
     "So với chính nó khi huấn luyện thông thường, trong điều kiện dữ liệu quy mô vừa"],
    ["Lượng tử hoá đánh đổi những gì?",
     "Giữa dung lượng, tốc độ và độ chính xác — và cái giá đó rơi vào nhóm vật thể nào"],
    ["mAP tổng phản ánh năng lực thật đến đâu?",
     "Đặc điểm nào của bộ dữ liệu khiến chỉ số này có nguy cơ gây hiểu nhầm"],
  ];
  qs.forEach(([q, sub], i) => {
    const y = 1.9 + i * 1.55;
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.6, y, w: 12.1, h: 1.28, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT },
    });
    s.addText(`CH 1.${i + 1}`, {
      x: 0.9, y: y + 0.2, w: 1.2, h: 0.4, fontFace: H, fontSize: 20, bold: true, color: AMBER, margin: 0,
    });
    s.addText(q, {
      x: 2.1, y: y + 0.17, w: 10.3, h: 0.42, fontFace: B, fontSize: 16, bold: true, color: NAVY, margin: 0,
    });
    s.addText(sub, {
      x: 2.1, y: y + 0.62, w: 10.3, h: 0.45, fontFace: B, fontSize: 13, color: GREY, margin: 0,
    });
  });
}

// ═══════════════════ 5 · SECTION: DỮ LIỆU ═══════════════════
{
  const s = darkSlide();
  s.addText("PHẦN 1", { x: 0.9, y: 2.6, w: 4, h: 0.3, fontFace: B, fontSize: 12, color: AMBER, bold: true, charSpacing: 2.5, margin: 0 });
  s.addText("Dữ liệu", { x: 0.9, y: 2.95, w: 8, h: 1.0, fontFace: H, fontSize: 44, bold: true, color: LIGHT, margin: 0 });
  s.addText("Bộ dữ liệu này không phải thứ nó trông như vậy", {
    x: 0.9, y: 4.0, w: 9, h: 0.5, fontFace: B, fontSize: 17, color: "9FB0C4", italic: true, margin: 0 });
}

// ═══════════════════ 6 · TỔNG QUAN DỮ LIỆU ═══════════════════
{
  const s = lightSlide("Bộ dữ liệu pkdarabi/cardetection", "Dữ liệu");
  stat(s, 0.6, 1.85, 2.85, "4.969", "ảnh, đồng nhất 416×416");
  stat(s, 3.7, 1.85, 2.85, "6.012", "hộp bao nhãn thật");
  stat(s, 6.8, 1.85, 2.85, "15", "lớp — đèn và giới hạn tốc độ");
  stat(s, 9.9, 1.85, 2.8, "1,21", "hộp bao trên mỗi ảnh");
  tableOf(s, 0.6, 3.75, 6.2, [
    [hdr("Tập"), hdr("Số ảnh"), hdr("Tỉ lệ"), hdr("Số hộp")],
    ["Huấn luyện", "3.530", "71,0%", "4.298"],
    ["Kiểm định", "801", "16,1%", "944"],
    ["Kiểm tra", "638", "12,8%", "770"],
  ], [1.9, 1.5, 1.4, 1.4]);
  bullets(s, 7.2, 3.75, 5.5, 2.0, [
    "Tên URL là “cardetection” nhưng không có lớp phương tiện nào",
    "Giữ nguyên 15 lớp gốc, không gộp, không ánh xạ lại",
    "Mật độ vật thể rất thưa so với TT100K hay Mapillary",
  ], 13);
  s.addNotes("Độ phân giải đồng nhất 416x416 là do Roboflow xử lý khi xuất — hệ quả: tăng imgsz khi train chủ yếu là phóng to.");
}

// ═══════════════════ 7 · MẤT CÂN BẰNG LỚP ═══════════════════
{
  const s = lightSlide("Mất cân bằng lớp 35,77 lần", "Phân tích khám phá");
  s.addImage({ path: img("eda_class_distribution.png"), x: 0.6, y: 1.7, w: 7.4, h: 4.55 });
  s.addShape(pres.ShapeType.roundRect, {
    x: 8.3, y: 1.9, w: 4.4, h: 1.3, fill: { color: RED }, rectRadius: 0.08, line: { color: RED } });
  s.addText("35,77×", { x: 8.3, y: 2.05, w: 4.4, h: 0.6, fontFace: H, fontSize: 32, bold: true, color: LIGHT, align: "center", margin: 0 });
  s.addText("Red Light (787) so với Speed Limit 10 (22)", {
    x: 8.5, y: 2.63, w: 4.0, h: 0.42, fontFace: B, fontSize: 11.5, color: "FFE0E0", align: "center", margin: 0 });
  bullets(s, 8.3, 3.5, 4.4, 2.5, [
    "Hai lớp đèn tín hiệu chiếm gần 26% tổng số hộp bao",
    "Speed Limit 10 chỉ có ~15 mẫu trong tập huấn luyện",
    "mAP lấy trung bình không trọng số nên lớp thiểu số kéo chỉ số xuống ngang lớp đa số",
  ], 12.5);
}

// ═══════════════════ 8 · TÍN HIỆU BẤT THƯỜNG ═══════════════════
{
  const s = lightSlide("Một tín hiệu bất thường về kích thước", "Phân tích khám phá");
  tableOf(s, 0.6, 1.9, 5.9, [
    [hdr("Nhóm kích thước"), hdr("Số hộp"), hdr("Tỉ lệ")],
    ["Nhỏ  (a < 0,01)", "2.122", "35,30%"],
    ["Trung bình", "806", "13,41%"],
    [{ text: "Lớn  (a ≥ 0,05)", options: { bold: true } },
     { text: "3.084", options: { bold: true } },
     { text: "51,30%", options: { bold: true, color: RED } }],
  ], [2.6, 1.7, 1.6], { rowH: 0.42 });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 4.05, w: 5.9, h: 1.55, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Vì sao đây là bất thường?", {
    x: 0.9, y: 4.22, w: 5.3, h: 0.35, fontFace: B, fontSize: 14, bold: true, color: NAVY, margin: 0 });
  s.addText("Biển báo chiếm hơn 5% diện tích khung hình nghĩa là xe đã ở rất gần biển. Trong cảnh đường thật, nhóm này hiếm khi chiếm quá bán.", {
    x: 0.9, y: 4.6, w: 5.3, h: 0.9, fontFace: B, fontSize: 12.5, color: GREY, margin: 0 });
  s.addImage({ path: img("eda_bbox_size_categories.png"), x: 6.9, y: 1.9, w: 5.8, h: 3.7 });
  s.addNotes("Đây là chỗ khởi phát toàn bộ mạch phân tích. Con số 51,30% dẫn tới việc soi lại thành phần bộ dữ liệu.");
}

// ═══════════════════ 9 · THÀNH PHẦN DATASET ═══════════════════
{
  const s = lightSlide("Bộ dữ liệu là một tập trộn từ nhiều nguồn", "Phát hiện");
  tableOf(s, 0.6, 1.9, 12.1, [
    [hdr("Nhóm nguồn"), hdr("Số ảnh"), hdr("Tỉ lệ"), hdr("Cạnh biển (trung vị)"), hdr("% vật thể nhỏ")],
    [{ text: "Ảnh cắt kiểu GTSRB", options: { bold: true } },
     { text: "1.922", options: { bold: true } },
     { text: "38,68%", options: { bold: true } },
     { text: "66,8% cạnh ảnh", options: { bold: true, color: RED } }, "0,0"],
    ["Ảnh số sáu chữ số", "1.586", "31,92%", "19,6%", "34,7"],
    ["Ảnh cảnh đường", "724", "14,57%", "13,4%", "31,1"],
    [{ text: "Camera mắt cá", options: { bold: true } }, "645", "12,98%",
     { text: "1,6%", options: { bold: true, color: RED } },
     { text: "99,6", options: { bold: true, color: RED } }],
    ["Nhóm khác", "92", "1,85%", "75,7%", "0,0"],
  ], [3.5, 1.8, 1.8, 3.2, 1.8], { rowH: 0.38 });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 5.05, w: 12.1, h: 1.1, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("Gần 39% số ảnh là ảnh cắt cận cảnh kiểu GTSRB — vốn dành cho bài toán PHÂN LỚP, không phải PHÁT HIỆN.", {
    x: 0.95, y: 5.2, w: 11.5, h: 0.35, fontFace: B, fontSize: 14.5, bold: true, color: AMBER, margin: 0 });
  s.addText("Phân bố kích thước vì vậy bị lưỡng cực: phân vị 25% là 20,8 điểm ảnh, phân vị 75% là 258,2 — chênh hơn mười hai lần, và vùng “biển thật trên đường” gần như trống.", {
    x: 0.95, y: 5.56, w: 11.5, h: 0.5, fontFace: B, fontSize: 12.5, color: "DCE3EC", margin: 0 });
}

// ═══════════════════ 10 · BA CHẾ ĐỘ ẢNH ═══════════════════
{
  const s = lightSlide("Ba chế độ ảnh cùng tồn tại", "Phát hiện");
  const capt = [
    ["Ảnh cắt kiểu GTSRB", "biển lấp gần kín khung hình"],
    ["Ảnh cảnh đường", "chế độ gần với thực tế nhất"],
    ["Camera mắt cá", "99,6% vật thể thuộc nhóm nhỏ"],
  ];
  ["sample_gtsrb_crop.jpg", "sample_road_scene.jpg", "sample_fisheye.jpg"].forEach((f, i) => {
    const x = 0.6 + i * 4.15;
    s.addImage({ path: img(f), x, y: 1.85, w: 3.8, h: 2.85 });
    s.addText(capt[i][0], { x, y: 4.85, w: 3.8, h: 0.32, fontFace: B, fontSize: 14, bold: true, color: NAVY, margin: 0 });
    s.addText(capt[i][1], { x, y: 5.18, w: 3.8, h: 0.55, fontFace: B, fontSize: 12, color: GREY, margin: 0 });
  });
  s.addText("Mô hình được dạy rất kỹ hai chế độ cực đoan, và thiếu hẳn chế độ trung gian vốn thường gặp nhất khi lái xe.", {
    x: 0.6, y: 5.95, w: 12.1, h: 0.4, fontFace: B, fontSize: 13.5, italic: true, color: NAVY, margin: 0 });
}

// ═══════════════════ 11 · RÒ RỈ DỮ LIỆU ═══════════════════
{
  const s = lightSlide("Rò rỉ dữ liệu giữa các tập", "Kiểm toán");
  stat(s, 0.6, 1.95, 3.7, "155", "nhóm ảnh nguồn ở nhiều hơn một tập");
  stat(s, 4.55, 1.95, 3.7, "101", "trong đó trùng byte hoàn toàn");
  stat(s, 8.5, 1.95, 4.2, "10,2%", "tập kiểm tra bị rò rỉ", RED);
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 3.75, w: 6.0, h: 2.35, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Hệ quả", { x: 0.9, y: 3.95, w: 5.4, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: NAVY, margin: 0 });
  bullets(s, 0.9, 4.35, 5.4, 1.6, [
    "65 / 638 ảnh kiểm tra có bản sao trong tập huấn luyện",
    "Chỉ còn 573 ảnh thực sự sạch",
    "Mọi con số mAP tuyệt đối nên hiểu là cận trên",
  ], 12.5);
  s.addShape(pres.ShapeType.roundRect, {
    x: 6.9, y: 3.75, w: 5.8, h: 2.35, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("Và rò rỉ KHÔNG phân bố đều", { x: 7.2, y: 3.95, w: 5.2, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: AMBER, margin: 0 });
  s.addTable([
    [{ text: "Phần", options: { bold: true, color: NAVY, fill: { color: AMBER } } },
     { text: "Nhỏ", options: { bold: true, color: NAVY, fill: { color: AMBER } } },
     { text: "Vừa", options: { bold: true, color: NAVY, fill: { color: AMBER } } },
     { text: "Lớn", options: { bold: true, color: NAVY, fill: { color: AMBER } } },
     { text: "% nhỏ", options: { bold: true, color: NAVY, fill: { color: AMBER } } }],
    [{ text: "65 ảnh rò rỉ", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "72", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "7", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "22", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "71,3%", options: { color: AMBER, bold: true, fill: { color: NAVY_2 } } }],
    [{ text: "573 ảnh sạch", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "154", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "163", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "352", options: { color: LIGHT, fill: { color: NAVY_2 } } },
     { text: "23,0%", options: { color: "DCE3EC", fill: { color: NAVY_2 } } }],
  ], {
    x: 7.2, y: 4.35, w: 5.2, colW: [1.7, 0.75, 0.75, 0.75, 1.25], rowH: 0.3,
    fontFace: B, fontSize: 10.5, align: "center", valign: "middle",
    border: { type: "solid", color: NAVY, pt: 1 }, margin: 3,
  });
  s.addText("Rò rỉ dồn gần hết vào nhóm vật thể nhỏ — đúng nhóm mà báo cáo này quan tâm nhất. Hệ quả được đo ở phần Kiểm chứng 1/2.", {
    x: 7.2, y: 5.35, w: 5.2, h: 0.6, fontFace: B, fontSize: 11.5, color: "DCE3EC", margin: 0, valign: "top" });
  s.addNotes("Nếu bị hỏi: bản trình bày trước từng nói 'rò rỉ ảnh hưởng như nhau tới mọi cấu hình'. Câu đó đúng ở mức thô nhưng sai ở mức chi tiết — nên đã bỏ, và thay bằng phép đo thật ở slide 23.");
}

// ═══════════════════ 12 · SECTION: PHƯƠNG PHÁP ═══════════════════
{
  const s = darkSlide();
  s.addText("PHẦN 2", { x: 0.9, y: 2.6, w: 4, h: 0.3, fontFace: B, fontSize: 12, color: AMBER, bold: true, charSpacing: 2.5, margin: 0 });
  s.addText("Phương pháp", { x: 0.9, y: 2.95, w: 9, h: 1.0, fontFace: H, fontSize: 44, bold: true, color: LIGHT, margin: 0 });
  s.addText("Năm cấu hình, một lượt chạy, một bộ tính độ đo", {
    x: 0.9, y: 4.0, w: 9, h: 0.5, fontFace: B, fontSize: 17, color: "9FB0C4", italic: true, margin: 0 });
}

// ═══════════════════ 13 · NĂM CẤU HÌNH ═══════════════════
{
  const s = lightSlide("Năm cấu hình khảo sát", "Thiết kế thực nghiệm");
  tableOf(s, 0.6, 1.85, 12.1, [
    [hdr("Cấu hình"), hdr("Vai trò"), hdr("Mục đích")],
    ["YOLO26s", "Thầy", "Cung cấp phân phối mềm; đồng thời là cận trên tham chiếu"],
    [{ text: "YOLO26n", options: { bold: true } }, { text: "Trò đối chứng", options: { bold: true } },
     { text: "Huấn luyện thông thường — mốc so sánh của giả thuyết chưng cất", options: { bold: true } }],
    ["YOLO26n + chưng cất", "Trò chưng cất", "Cấu hình cần đánh giá của giả thuyết thứ nhất"],
    ["ONNX FP32", "Xuất từ trò KD", "Cô lập ảnh hưởng của việc đổi môi trường thực thi"],
    ["ONNX INT8", "Xuất từ trò KD", "Cấu hình cần đánh giá của giả thuyết thứ hai"],
  ], [3.2, 2.5, 6.4], { rowH: 0.42, fs: 12.5 });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 5.05, w: 12.1, h: 1.05, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Vì sao cần mốc ONNX FP32 ở giữa?", {
    x: 0.9, y: 5.2, w: 11.5, h: 0.32, fontFace: B, fontSize: 14, bold: true, color: NAVY, margin: 0 });
  s.addText("Nếu chỉ so INT8 với mô hình PyTorch gốc, chênh lệch sẽ trộn lẫn hai nguyên nhân: đổi môi trường thực thi và lượng tử hoá. Mốc trung gian tách được hai thứ đó ra.", {
    x: 0.9, y: 5.55, w: 11.5, h: 0.45, fontFace: B, fontSize: 12.5, color: GREY, margin: 0 });
}

// ═══════════════════ 14 · SIÊU THAM SỐ ═══════════════════
{
  const s = lightSlide("Siêu tham số và một yếu tố gây nhiễu", "Thiết kế thực nghiệm");
  tableOf(s, 0.6, 1.85, 6.5, [
    [hdr("Tham số"), hdr("Giá trị")],
    ["Số chu kỳ (thầy / đối chứng / KD)", "50 / 50 / 50"],
    [{ text: "Kích thước lô", options: { bold: true } },
     { text: "16 / 24 / 8", options: { bold: true, color: RED } }],
    ["Hệ số chưng cất", "6,0 (mặc định)"],
    ["Kích thước ảnh", "640"],
    ["Hạt ngẫu nhiên", "42"],
    ["Ngưỡng tin cậy khi đo", "0,001"],
    ["Ảnh hiệu chuẩn INT8", "300"],
  ], [4.3, 2.2], { rowH: 0.38, fs: 12 });
  s.addShape(pres.ShapeType.roundRect, {
    x: 7.5, y: 1.85, w: 5.2, h: 2.5, fill: { color: RED }, rectRadius: 0.08, line: { color: RED } });
  s.addText("Yếu tố gây nhiễu chưa kiểm soát được", {
    x: 7.8, y: 2.05, w: 4.6, h: 0.6, fontFace: B, fontSize: 14.5, bold: true, color: LIGHT, margin: 0 });
  s.addText("Nhánh chưng cất chạy với lô 8, nhánh đối chứng dùng 24 — do phải nạp đồng thời cả hai mô hình vào VRAM.\n\nVì vậy kết luận đúng mực là “trong cấu hình này chưng cất không có lợi”, KHÔNG phải “chưng cất có hại”.", {
    x: 7.8, y: 2.7, w: 4.6, h: 1.5, fontFace: B, fontSize: 12, color: "FFE4E4", margin: 0, valign: "top" });
  s.addShape(pres.ShapeType.roundRect, {
    x: 7.5, y: 4.6, w: 5.2, h: 1.55, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Đối chứng đúng nghĩa", {
    x: 7.8, y: 4.78, w: 4.6, h: 0.32, fontFace: B, fontSize: 14, bold: true, color: NAVY, margin: 0 });
  s.addText("Mô hình trò được huấn luyện HAI LẦN với cùng số chu kỳ, cùng hạt ngẫu nhiên, cùng kích thước ảnh — chỉ khác ở việc bật hay tắt chưng cất.", {
    x: 7.8, y: 5.12, w: 4.6, h: 0.95, fontFace: B, fontSize: 12, color: GREY, margin: 0, valign: "top" });
}

// ═══════════════════ 15 · AP THEO KÍCH THƯỚC ═══════════════════
{
  const s = lightSlide("Công cụ trung tâm: AP tách theo kích thước", "Độ đo");
  s.addText("mAP tổng lấy trung bình trên các lớp nhưng KHÔNG phân biệt kích thước vật thể.", {
    x: 0.6, y: 1.62, w: 12.1, h: 0.35, fontFace: B, fontSize: 15, color: GREY, margin: 0 });
  const boxes = [
    ["AP nhỏ", "a < 32²", "Biển ở xa — nhóm quyết định thời gian phản ứng", RED],
    ["AP trung bình", "32² ≤ a < 96²", "Vùng chuyển tiếp", AMBER],
    ["AP lớn", "a ≥ 96²", "Biển gần — nhóm dễ, thường đã bão hoà", GREEN],
  ];
  boxes.forEach(([t, r, d, c], i) => {
    const x = 0.6 + i * 4.15;
    s.addShape(pres.ShapeType.roundRect, { x, y: 2.2, w: 3.8, h: 2.0, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.28, y: 2.45, w: 0.5, h: 0.5, fill: { color: c }, line: { color: c } });
    s.addText(t, { x: x + 0.95, y: 2.5, w: 2.6, h: 0.4, fontFace: B, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addText(r, { x: x + 0.28, y: 3.1, w: 3.2, h: 0.32, fontFace: B, fontSize: 13, color: c, bold: true, margin: 0 });
    s.addText(d, { x: x + 0.28, y: 3.45, w: 3.2, h: 0.65, fontFace: B, fontSize: 12, color: GREY, margin: 0 });
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 4.55, w: 12.1, h: 1.5, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("Vì sao bắt buộc phải tách?", {
    x: 0.95, y: 4.75, w: 11.5, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: AMBER, margin: 0 });
  s.addText("51,30% hộp bao trong bộ dữ liệu thuộc nhóm LỚN — nhóm mà mọi cấu hình đều xử lý tốt như nhau. Chúng chi phối giá trị trung bình và pha loãng mọi suy giảm ở nhóm khó. Câu hỏi mà mAP tổng không trả lời được: khi mô hình kém đi, phần kém đó rơi vào nhóm nào?", {
    x: 0.95, y: 5.12, w: 11.5, h: 0.8, fontFace: B, fontSize: 13, color: "DCE3EC", margin: 0 });
}

// ═══════════════════ 16 · NGƯỠNG CHẤP NHẬN ═══════════════════
{
  const s = lightSlide("Ngưỡng chấp nhận khai báo trước khi chạy", "Thiết kế thực nghiệm");
  s.addText("Năm tiêu chí được viết vào ô cấu hình đầu tiên của sổ tay, TRƯỚC khi có bất kỳ số liệu nào.", {
    x: 0.6, y: 1.62, w: 12.1, h: 0.35, fontFace: B, fontSize: 15, color: GREY, margin: 0 });
  const th = [
    "Mô hình chưng cất không được kém đối chứng quá 0,005 điểm mAP@0,5:0,95",
    "Mô hình chưng cất được kỳ vọng TỐT HƠN đối chứng",
    "Bản INT8 không được giảm quá 0,015 điểm mAP so với FP32",
    "Bản INT8 phải nhỏ hơn FP32 ít nhất 50% dung lượng",
    "Mô hình trò phải nhẹ hơn mô hình thầy",
  ];
  th.forEach((t, i) => {
    const y = 2.25 + i * 0.66;
    s.addShape(pres.ShapeType.ellipse, { x: 0.7, y, w: 0.38, h: 0.38, fill: { color: AMBER }, line: { color: AMBER } });
    s.addText(String(i + 1), { x: 0.7, y: y + 0.03, w: 0.38, h: 0.32, fontFace: B, fontSize: 13, bold: true, color: NAVY, align: "center", margin: 0 });
    s.addText(t, { x: 1.25, y: y + 0.02, w: 11.4, h: 0.35, fontFace: B, fontSize: 14, color: INK, margin: 0 });
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 5.72, w: 12.1, h: 0.72, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Cách làm này buộc người thực hiện cam kết tiêu chí trước khi nhìn thấy số liệu — ngăn việc diễn giải lại kỳ vọng cho khớp kết quả.", {
    x: 0.95, y: 5.9, w: 11.5, h: 0.42, fontFace: B, fontSize: 13, italic: true, color: NAVY, margin: 0 });
}

// ═══════════════════ 17 · SECTION: KẾT QUẢ ═══════════════════
{
  const s = darkSlide();
  s.addText("PHẦN 3", { x: 0.9, y: 2.6, w: 4, h: 0.3, fontFace: B, fontSize: 12, color: AMBER, bold: true, charSpacing: 2.5, margin: 0 });
  s.addText("Kết quả", { x: 0.9, y: 2.95, w: 9, h: 1.0, fontFace: H, fontSize: 44, bold: true, color: LIGHT, margin: 0 });
  s.addText("Hai kết quả âm và một phát hiện", {
    x: 0.9, y: 4.0, w: 9, h: 0.5, fontFace: B, fontSize: 17, color: "9FB0C4", italic: true, margin: 0 });
}

// ═══════════════════ 18 · BẢNG KẾT QUẢ ═══════════════════
{
  const s = lightSlide("Kết quả năm cấu hình trên tập kiểm tra", "Kết quả");
  tableOf(s, 0.6, 1.9, 12.1, [
    [hdr("Cấu hình"), hdr("Tệp (MB)"), hdr("mAP@0,5"), hdr("mAP@.5:.95"), hdr("AP nhỏ"), hdr("AP lớn"), hdr("FPS")],
    ["YOLO26s (thầy)", "19,39", "0,9520", "0,7822", "0,616", "0,859", "74,4"],
    [{ text: "YOLO26n đối chứng", options: { bold: true } }, { text: "5,15", options: { bold: true } },
     { text: "0,9348", options: { bold: true } }, { text: "0,7773", options: { bold: true } },
     { text: "0,548", options: { bold: true } }, { text: "0,862", options: { bold: true } },
     { text: "69,7", options: { bold: true } }],
    ["YOLO26n chưng cất", "5,15", { text: "0,9014", options: { color: RED } }, "0,7450",
     { text: "0,486", options: { color: RED } }, "0,852", "74,8"],
    ["ONNX FP32", "9,35", "0,9079", "0,7473", "0,462", "0,847", "19,8"],
    ["ONNX INT8", "2,78", "0,9041", "0,7437", { text: "0,437", options: { color: RED } }, "0,839", "9,4"],
  ], [3.0, 1.5, 1.65, 1.85, 1.4, 1.4, 1.3], { rowH: 0.4, fs: 11.5 });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 4.85, w: 12.1, h: 1.25, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("Đọc theo cột mAP@0,5, mọi cấu hình nằm gọn trong dải 0,90–0,95 — khoảng cách trông khiêm tốn.", {
    x: 0.95, y: 5.02, w: 11.5, h: 0.35, fontFace: B, fontSize: 14, color: "DCE3EC", margin: 0 });
  s.addText("Đọc theo cột AP nhỏ, dải trải từ 0,437 đến 0,616 — chênh lệch tương đối lớn gấp nhiều lần.", {
    x: 0.95, y: 5.4, w: 11.5, h: 0.35, fontFace: B, fontSize: 14.5, bold: true, color: AMBER, margin: 0 });
  s.addText("Cột AP lớn: cả ba mô hình PyTorch đều quanh 0,85–0,86 — với vật thể lớn thì bài toán đã bão hoà.", {
    x: 0.95, y: 5.75, w: 11.5, h: 0.3, fontFace: B, fontSize: 12, color: "9FB0C4", italic: true, margin: 0 });
}

// ═══════════════════ 19 · CHƯNG CẤT: KẾT QUẢ ÂM ═══════════════════
{
  const s = lightSlide("Chưng cất tri thức: kết quả âm", "Kết quả · Giả thuyết 1");
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 1.9, w: 3.85, h: 1.75, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("0,9348", { x: 0.6, y: 2.15, w: 3.85, h: 0.7, fontFace: H, fontSize: 36, bold: true, color: NAVY, align: "center", margin: 0 });
  s.addText("Trò ĐỐI CHỨNG\nhuấn luyện thông thường", { x: 0.75, y: 2.85, w: 3.55, h: 0.65, fontFace: B, fontSize: 12, color: GREY, align: "center", margin: 0 });
  s.addText("▶", { x: 4.6, y: 2.5, w: 0.6, h: 0.5, fontFace: B, fontSize: 24, color: AMBER, align: "center", margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 5.3, y: 1.9, w: 3.85, h: 1.75, fill: { color: RED }, rectRadius: 0.08, line: { color: RED } });
  s.addText("0,9014", { x: 5.3, y: 2.15, w: 3.85, h: 0.7, fontFace: H, fontSize: 36, bold: true, color: LIGHT, align: "center", margin: 0 });
  s.addText("Trò CHƯNG CẤT\nhọc từ YOLO26s", { x: 5.45, y: 2.85, w: 3.55, h: 0.65, fontFace: B, fontSize: 12, color: "FFE4E4", align: "center", margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 9.3, y: 1.9, w: 3.4, h: 1.75, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("−3,34", { x: 9.3, y: 2.15, w: 3.4, h: 0.7, fontFace: H, fontSize: 34, bold: true, color: AMBER, align: "center", margin: 0 });
  s.addText("điểm phần trăm mAP@0,5\n(−6,20 ở AP nhỏ)", { x: 9.45, y: 2.85, w: 3.1, h: 0.65, fontFace: B, fontSize: 12, color: "DCE3EC", align: "center", margin: 0 });

  s.addText("Ba cách giải thích khả dĩ", { x: 0.6, y: 3.95, w: 12.1, h: 0.35, fontFace: B, fontSize: 16, bold: true, color: NAVY, margin: 0 });
  numbered(s, 0.6, 4.45, 3.9, 1, "Khoảng cách quá hẹp", "Thầy chỉ hơn trò 1,72 điểm — tri thức truyền được không bù nổi chi phí nhiễu");
  numbered(s, 4.7, 4.45, 3.9, 2, "Kích thước lô lệch", "Lô 8 so với 24 — yếu tố gây nhiễu chưa kiểm soát được");
  numbered(s, 8.8, 4.45, 3.9, 3, "Hệ số 6,0 quá lớn", "Thành phần bắt chước có thể lấn át tín hiệu từ nhãn cứng");
}

// ═══════════════════ 20 · XÁC MINH KD THẬT SỰ CHẠY ═══════════════════
{
  const s = lightSlide("Chưng cất có thực sự được kích hoạt không?", "Kết quả · Xác minh");
  s.addText("Trước khi diễn giải một kết quả âm, phải loại trừ khả năng cơ chế không hề chạy — nếu không, ta chỉ đang so sánh hai lần huấn luyện thông thường với kích thước lô khác nhau.", {
    x: 0.6, y: 1.62, w: 12.1, h: 0.62, fontFace: B, fontSize: 14.5, color: GREY, margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 2.5, w: 6.0, h: 2.5, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Bằng chứng", { x: 0.9, y: 2.7, w: 5.4, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: NAVY, margin: 0 });
  s.addText("Nhật ký huấn luyện của nhánh chưng cất có thêm cột train/dis_loss — cột này KHÔNG tồn tại ở nhánh đối chứng.", {
    x: 0.9, y: 3.08, w: 5.4, h: 0.8, fontFace: B, fontSize: 13, color: INK, margin: 0, valign: "top" });
  s.addText("Kết luận: hàm mất mát chưng cất đã hoạt động và đã hội tụ. Kết quả âm là kết quả thật, không phải lỗi cấu hình.", {
    x: 0.9, y: 3.95, w: 5.4, h: 0.85, fontFace: B, fontSize: 13, italic: true, color: NAVY, margin: 0, valign: "top" });
  s.addShape(pres.ShapeType.roundRect, { x: 7.0, y: 2.5, w: 5.7, h: 2.5, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("train/dis_loss", { x: 7.3, y: 2.7, w: 5.1, h: 0.35, fontFace: B, fontSize: 14, bold: true, color: AMBER, margin: 0 });
  s.addText("12,1663", { x: 7.3, y: 3.1, w: 2.4, h: 0.6, fontFace: H, fontSize: 30, bold: true, color: LIGHT, align: "center", margin: 0 });
  s.addText("chu kỳ đầu", { x: 7.3, y: 3.7, w: 2.4, h: 0.3, fontFace: B, fontSize: 11.5, color: "9FB0C4", align: "center", margin: 0 });
  s.addText("→", { x: 9.7, y: 3.18, w: 0.6, h: 0.5, fontFace: B, fontSize: 24, color: AMBER, align: "center", margin: 0 });
  s.addText("1,1608", { x: 10.2, y: 3.1, w: 2.2, h: 0.6, fontFace: H, fontSize: 30, bold: true, color: AMBER, align: "center", margin: 0 });
  s.addText("chu kỳ cuối", { x: 10.2, y: 3.7, w: 2.2, h: 0.3, fontFace: B, fontSize: 11.5, color: "9FB0C4", align: "center", margin: 0 });
  s.addText("Xu hướng giảm đơn điệu — cơ chế hội tụ bình thường.", {
    x: 7.3, y: 4.2, w: 5.1, h: 0.6, fontFace: B, fontSize: 12.5, color: "DCE3EC", margin: 0 });
}

// ═══════════════════ 21 · LƯỢNG TỬ HOÁ ═══════════════════
{
  const s = lightSlide("Lượng tử hoá: được gì, mất gì", "Kết quả · Giả thuyết 2");
  tableOf(s, 0.6, 1.9, 7.2, [
    [hdr("Cấu hình"), hdr("Tệp (MB)"), hdr("mAP@0,5"), hdr("Trung vị (ms)"), hdr("p95 (ms)")],
    ["PyTorch FP16", "5,15", "0,9014", "13,37", "14,33"],
    ["ONNX FP32", "9,35", "0,9079", "50,41", "55,76"],
    [{ text: "ONNX INT8", options: { bold: true } },
     { text: "2,78", options: { bold: true, color: GREEN } }, "0,9041",
     { text: "106,90", options: { bold: true, color: RED } },
     { text: "112,88", options: { bold: true, color: RED } }],
  ], [1.9, 1.4, 1.4, 1.5, 1.0], { rowH: 0.42, fs: 11.5 });
  s.addShape(pres.ShapeType.roundRect, { x: 8.1, y: 1.9, w: 2.2, h: 1.45, fill: { color: GREEN }, rectRadius: 0.08, line: { color: GREEN } });
  s.addText("−70,3%", { x: 8.1, y: 2.1, w: 2.2, h: 0.6, fontFace: H, fontSize: 24, bold: true, color: LIGHT, align: "center", margin: 0 });
  s.addText("dung lượng\nĐẠT mục tiêu", { x: 8.15, y: 2.68, w: 2.1, h: 0.6, fontFace: B, fontSize: 11, color: "DFF2E7", align: "center", margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 10.5, y: 1.9, w: 2.2, h: 1.45, fill: { color: RED }, rectRadius: 0.08, line: { color: RED } });
  s.addText("8×", { x: 10.5, y: 2.1, w: 2.2, h: 0.6, fontFace: H, fontSize: 24, bold: true, color: LIGHT, align: "center", margin: 0 });
  s.addText("CHẬM hơn\nbản PyTorch gốc", { x: 10.55, y: 2.68, w: 2.1, h: 0.6, fontFace: B, fontSize: 11, color: "FFE4E4", align: "center", margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 3.85, w: 12.1, h: 2.25, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Vì sao INT8 lại chậm hơn?", { x: 0.95, y: 4.05, w: 11.4, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: NAVY, margin: 0 });
  bullets(s, 0.95, 4.45, 11.4, 1.5, [
    "Lợi ích tốc độ của số nguyên 8 bit chỉ hiện thực hoá khi môi trường thực thi có nhân tính toán số nguyên được tối ưu cho phần cứng đích",
    "Nếu không, thời gian tiết kiệm được bị tiêu hết vào các phép chuyển đổi lượng tử hoá và giải lượng tử hoá xen giữa các lớp",
    "Bản ONNX FP32 đã chậm hơn PyTorch gần bốn lần TRƯỚC khi lượng tử hoá — đó là chi phí của việc đổi môi trường, và mốc trung gian giúp tách được hai nguyên nhân",
  ], 12.5);
}

// ═══════════════════ 22 · PHÁT HIỆN CHÍNH ═══════════════════
{
  const s = darkSlide();
  s.addText("PHÁT HIỆN CHÍNH", { x: 0.7, y: 0.5, w: 8, h: 0.3, fontFace: B, fontSize: 12, color: AMBER, bold: true, charSpacing: 2.5, margin: 0 });
  s.addText("mAP tổng che giấu chi phí thật", {
    x: 0.7, y: 0.88, w: 12, h: 0.75, fontFace: H, fontSize: 33, bold: true, color: LIGHT, margin: 0 });
  const rows = [
    ["Chưng cất tri thức", "−0,0334", "−0,0620", "1,85×"],
    ["Lượng tử hoá INT8", "−0,0038", "−0,0247", "6,5×"],
  ];
  s.addTable([
    [{ text: "Phép can thiệp", options: { bold: true, color: NAVY, fill: { color: AMBER } } },
     { text: "Δ mAP@0,5", options: { bold: true, color: NAVY, fill: { color: AMBER } } },
     { text: "Δ AP nhỏ", options: { bold: true, color: NAVY, fill: { color: AMBER } } },
     { text: "Tỉ số", options: { bold: true, color: NAVY, fill: { color: AMBER } } }],
    ...rows.map((r, i) => r.map((c, j) => ({
      text: c,
      options: { color: j === 3 ? AMBER : LIGHT, bold: j === 3 || (i === 1 && j > 0), fill: { color: NAVY_2 } },
    }))),
  ], {
    x: 0.7, y: 1.95, w: 12.0, colW: [4.2, 2.6, 2.6, 2.6], rowH: 0.52,
    fontFace: B, fontSize: 15, align: "center", valign: "middle",
    border: { type: "solid", color: NAVY, pt: 1.5 }, margin: 5,
  });
  s.addShape(pres.ShapeType.roundRect, { x: 0.7, y: 3.75, w: 12.0, h: 1.35, fill: { color: RED }, rectRadius: 0.08, line: { color: RED } });
  s.addText("“Giảm 70% dung lượng, chỉ mất 0,4% mAP” — nghe như miễn phí.", {
    x: 1.05, y: 3.92, w: 11.3, h: 0.4, fontFace: B, fontSize: 16, color: "FFD9D9", italic: true, margin: 0 });
  s.addText("Thực chất mất 2,47 điểm phần trăm ở nhóm vật thể nhỏ — gấp 6,5 lần.", {
    x: 1.05, y: 4.35, w: 11.3, h: 0.45, fontFace: B, fontSize: 19, bold: true, color: LIGHT, margin: 0 });
  s.addText("Cơ chế đã được dự đoán từ lý thuyết: sai số lượng tử hoá tác động lên toàn bộ bản đồ đặc trưng, trong khi vật thể nhỏ vốn chỉ để lại tín hiệu yếu — nên tỉ lệ tín hiệu trên nhiễu của chúng suy giảm nhiều hơn. Quan sát thực nghiệm khớp với dự đoán làm tăng độ tin cậy của kết luận.", {
    x: 0.7, y: 5.35, w: 12.0, h: 1.0, fontFace: B, fontSize: 13, color: "9FB0C4", margin: 0, valign: "top" });
  s.addNotes("Đây là slide quan trọng nhất của báo cáo. Nếu chỉ nhớ một điều thì nhớ con số 6,5 lần. Phản biện hiển nhiên nhất — 'dữ liệu có rò rỉ thì số này còn nghĩa gì' — được trả lời ngay ở slide sau.");
}

// ═══════════════════ 23 · ĐO LẠI TRÊN TẬP SẠCH ═══════════════════
{
  const s = lightSlide("Luận điểm có sống sót trên dữ liệu sạch không?", "Kiểm chứng 1/2");
  s.addText("Toàn bộ được đo lại tại chỗ bằng src/evaluation/coco_eval.py, độc lập với sổ tay Kaggle.", {
    x: 0.6, y: 1.5, w: 12.1, h: 0.32, fontFace: B, fontSize: 13, italic: true, color: GREY, margin: 0 });

  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 1.95, w: 5.9, h: 1.75, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Trước hết: số cũ có tái lập được không?", { x: 0.9, y: 2.12, w: 5.3, h: 0.32, fontFace: B, fontSize: 14, bold: true, color: NAVY, margin: 0 });
  s.addText("Ba cấu hình PyTorch khớp ĐẾN BỐN CHỮ SỐ: 0,9520 · 0,9348 · 0,9014.", {
    x: 0.9, y: 2.5, w: 5.3, h: 0.42, fontFace: B, fontSize: 12.5, color: INK, margin: 0, valign: "top" });
  s.addText("Ngoại lệ: INT8 cho 0,9107 thay vì 0,9041, và bản ONNX FP32 không có sẵn — nên phép so sánh INT8↔FP32 CHƯA được tái lập độc lập.", {
    x: 0.9, y: 2.96, w: 5.3, h: 0.64, fontFace: B, fontSize: 12, color: RED, margin: 0, valign: "top" });

  s.addShape(pres.ShapeType.roundRect, { x: 6.8, y: 1.95, w: 5.9, h: 1.75, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Bỏ 65 ảnh rò rỉ thì điều gì xảy ra?", { x: 7.1, y: 2.12, w: 5.3, h: 0.32, fontFace: B, fontSize: 14, bold: true, color: NAVY, margin: 0 });
  s.addText("mAP tổng TĂNG ở cả bốn cấu hình — vì phần bị bỏ là phần khó nhất.", {
    x: 7.1, y: 2.5, w: 5.3, h: 0.42, fontFace: B, fontSize: 12.5, color: INK, margin: 0, valign: "top" });
  s.addText("AP nhỏ GIẢM ở cả bốn — vì đúng những hộp nhỏ được ghi nhớ đã bị lấy đi (71,3% phần rò rỉ là vật thể nhỏ).", {
    x: 7.1, y: 2.96, w: 5.3, h: 0.64, fontFace: B, fontSize: 12, color: INK, margin: 0, valign: "top" });

  const rows = [
    ["638 ảnh (có rò rỉ)", "0,0334", "0,0620", "1,85×"],
    ["573 ảnh sạch", "0,0131", "0,0347", "2,66×"],
  ];
  s.addTable([
    [{ text: "Tập đánh giá", options: { bold: true, color: LIGHT, fill: { color: NAVY } } },
     { text: "Sụt mAP@0,5", options: { bold: true, color: LIGHT, fill: { color: NAVY } } },
     { text: "Sụt AP nhỏ", options: { bold: true, color: LIGHT, fill: { color: NAVY } } },
     { text: "Tỉ số", options: { bold: true, color: LIGHT, fill: { color: NAVY } } }],
    ...rows.map((r, i) => r.map((c, j) => ({
      text: c,
      options: { color: j === 3 ? (i === 1 ? GREEN : GREY) : INK, bold: i === 1, fill: { color: i === 1 ? "E8F3ED" : "FFFFFF" } },
    }))),
  ], {
    x: 0.6, y: 3.95, w: 12.1, colW: [4.3, 2.6, 2.6, 2.6], rowH: 0.44,
    fontFace: B, fontSize: 14, align: "center", valign: "middle",
    border: { type: "solid", color: "DDE2E8", pt: 1 }, margin: 5,
  });

  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 5.5, w: 12.1, h: 1.05, fill: { color: GREEN }, rectRadius: 0.08, line: { color: GREEN } });
  s.addText("Trên dữ liệu sạch, tỉ số TĂNG từ 1,85 lên 2,66 lần.", {
    x: 0.95, y: 5.66, w: 11.5, h: 0.38, fontFace: B, fontSize: 17, bold: true, color: LIGHT, margin: 0 });
  s.addText("Hiện tượng “mAP tổng che giấu chi phí thật” không phải tạo tác của dữ liệu bẩn — làm sạch dữ liệu chỉ khiến nó rõ hơn.", {
    x: 0.95, y: 6.06, w: 11.5, h: 0.38, fontFace: B, fontSize: 13, color: "DFF0E6", margin: 0 });
  s.addNotes("Slide này tồn tại vì phản biện dễ đoán nhất là 'dataset rò rỉ 10% thì kết luận còn giá trị gì'. Câu trả lời: đã đo, và kết luận mạnh lên. Nếu bị hỏi tại sao mAP lại tăng khi bỏ ảnh đã học thuộc — vì 71,3% phần rò rỉ là vật thể nhỏ, tức phần khó nhất, bỏ đi thì tập còn lại dễ hơn.");
}

// ═══════════════════ 24 · NGƯỠNG CHẤP NHẬN ═══════════════════
{
  const s = lightSlide("Kiểm tra ngưỡng: 3 đạt, 2 không đạt", "Kết quả");
  const rows = [
    ["KD không kém đối chứng quá 0,005 điểm", "Δ = −0,0323", false],
    ["KD tốt hơn đối chứng (kỳ vọng ban đầu)", "Δ = −0,0323", false],
    ["INT8 giảm không quá 0,015 điểm so với FP32", "giảm 0,0036", true],
    ["INT8 nhỏ hơn FP32 ít nhất 50%", "giảm 70,3%", true],
    ["Trò chưng cất nhẹ hơn thầy", "5,15 so với 19,39 MB", true],
  ];
  rows.forEach(([t, v, ok], i) => {
    const y = 1.95 + i * 0.78;
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y, w: 12.1, h: 0.66, fill: { color: TINT }, rectRadius: 0.06, line: { color: TINT } });
    s.addShape(pres.ShapeType.ellipse, { x: 0.85, y: y + 0.14, w: 0.38, h: 0.38, fill: { color: ok ? GREEN : RED }, line: { color: ok ? GREEN : RED } });
    s.addText(ok ? "✓" : "✕", { x: 0.85, y: y + 0.17, w: 0.38, h: 0.32, fontFace: B, fontSize: 14, bold: true, color: LIGHT, align: "center", margin: 0 });
    s.addText(t, { x: 1.45, y: y + 0.16, w: 7.4, h: 0.35, fontFace: B, fontSize: 13.5, color: INK, margin: 0 });
    s.addText(v, { x: 8.9, y: y + 0.16, w: 2.2, h: 0.35, fontFace: B, fontSize: 13, color: GREY, margin: 0 });
    s.addText(ok ? "ĐẠT" : "KHÔNG ĐẠT", { x: 11.1, y: y + 0.16, w: 1.4, h: 0.35, fontFace: B, fontSize: 12.5, bold: true, color: ok ? GREEN : RED, align: "right", margin: 0 });
  });
  s.addText("Cả hai ngưỡng không đạt đều thuộc về giả thuyết chưng cất. Việc khai báo tiêu chí trước và báo cáo đầy đủ cả kết quả không đạt là cách làm đúng đắn về mặt phương pháp.", {
    x: 0.6, y: 5.95, w: 12.1, h: 0.5, fontFace: B, fontSize: 13, italic: true, color: NAVY, margin: 0 });
}

// ═══════════════════ 25 · SECTION: VIDEO ═══════════════════
{
  const s = darkSlide();
  s.addText("PHẦN 4", { x: 0.9, y: 2.6, w: 4, h: 0.3, fontFace: B, fontSize: 12, color: AMBER, bold: true, charSpacing: 2.5, margin: 0 });
  s.addText("Kiểm chứng trên video thật", { x: 0.9, y: 2.95, w: 11, h: 1.0, fontFace: H, fontSize: 44, bold: true, color: LIGHT, margin: 0 });
  s.addText("Kiểm chứng 2/2 — dữ liệu ngoài phân bố huấn luyện, không có nhãn thật", {
    x: 0.9, y: 4.0, w: 11, h: 0.5, fontFace: B, fontSize: 17, color: "9FB0C4", italic: true, margin: 0 });
  s.addText("Kiểm chứng 1/2 đã loại phản biện “dữ liệu bẩn”. Phần này loại phản biện “chỉ đúng trên đúng tập kiểm tra đó”.", {
    x: 0.9, y: 4.55, w: 11, h: 0.4, fontFace: B, fontSize: 13, color: "6E819A", margin: 0 });
}

// ═══════════════════ 26 · THIẾT KẾ KIỂM CHỨNG ═══════════════════
{
  const s = lightSlide("Thiết kế: một dự đoán có thể sai", "Kiểm chứng video");
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 1.72, w: 12.1, h: 1.05, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("Ba video KHÔNG có nhãn thật, nên phép kiểm chứng này không báo cáo mAP — làm vậy sẽ là bịa số.", {
    x: 0.95, y: 1.87, w: 11.5, h: 0.35, fontFace: B, fontSize: 14, color: AMBER, bold: true, margin: 0 });
  s.addText("Thay vào đó: nếu điểm yếu thật nằm ở vật thể nhỏ, thì tăng độ phân giải đầu vào phải làm lộ thêm các phát hiện CÓ CẠNH NHỎ một cách chọn lọc — chứ không tăng đều ở mọi cỡ.", {
    x: 0.95, y: 2.25, w: 11.5, h: 0.45, fontFace: B, fontSize: 13, color: "DCE3EC", margin: 0 });
  tableOf(s, 0.6, 3.1, 5.9, [
    [hdr("Video"), hdr("Độ phân giải"), hdr("Số khung")],
    ["A.mp4", "1660×1244", "121"],
    ["B.mp4", "1280×720", "240"],
    ["download.mp4", "1080×1920", "500"],
  ], [2.2, 2.2, 1.5], { rowH: 0.38 });
  s.addText("Ba cấu hình so sánh", { x: 6.9, y: 3.1, w: 5.8, h: 0.32, fontFace: B, fontSize: 15, bold: true, color: NAVY, margin: 0 });
  numbered(s, 6.9, 3.55, 5.8, 1, "A · imgsz 640, conf 0,35", "Mặc định cũ, không cắt vùng quan tâm");
  numbered(s, 6.9, 4.5, 5.8, 2, "B · imgsz 1280, conf 0,20", "Cắt bỏ 30% đáy khung hình");
  numbered(s, 6.9, 5.45, 5.8, 3, "C · 1280 + suy luận theo lát cắt", "Ô 640 chồng lấn 20%, gộp bằng NMS");
  s.addText("Dùng CHÍNH mô hình học trò được chưng cất — cấu hình trung tâm của báo cáo.", {
    x: 0.6, y: 6.3, w: 5.9, h: 0.35, fontFace: B, fontSize: 12, italic: true, color: NAVY, margin: 0 });
}

// ═══════════════════ 27 · KẾT QUẢ VIDEO ═══════════════════
{
  const s = lightSlide("Mức tăng phân bố hoàn toàn không đều", "Kiểm chứng video");
  tableOf(s, 0.6, 1.85, 6.3, [
    [hdr("Nhóm cạnh hộp"), hdr("A"), hdr("B"), hdr("C"), hdr("A→C")],
    [{ text: "Rất nhỏ (<2%)", options: { bold: true } }, "8", "82", "104",
     { text: "13,0×", options: { bold: true, color: RED } }],
    [{ text: "Nhỏ (2–4%)", options: { bold: true } }, "40", "122", "171",
     { text: "4,3×", options: { bold: true, color: RED } }],
    ["Vừa (4–8%)", "61", "114", "142", { text: "2,3×", options: { color: GREY } }],
    ["Lớn (≥8%)", "15", "10", "8", { text: "0,5×", options: { bold: true, color: GREEN } }],
  ], [2.1, 1.0, 1.0, 1.0, 1.2], { rowH: 0.42, fs: 12 });
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 4.15, w: 6.3, h: 1.95, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("13,0×   →   4,3×   →   2,3×   →   0,5×", {
    x: 0.9, y: 4.32, w: 5.7, h: 0.45, fontFace: H, fontSize: 19, bold: true, color: AMBER, margin: 0 });
  s.addText("Tỉ lệ tăng GIẢM ĐƠN ĐIỆU theo kích thước. Nhóm nhỏ nhất tăng gấp mười ba lần; nhóm lớn nhất thậm chí GIẢM một nửa. Nhiễu ngẫu nhiên phân bố đều — không tạo ra được hình dạng này.", {
    x: 0.9, y: 4.88, w: 5.7, h: 1.05, fontFace: B, fontSize: 12.5, color: "DCE3EC", margin: 0, valign: "top" });
  s.addImage({ path: img("video_size_dist.png"), x: 7.2, y: 2.0, w: 5.5, h: 2.0 });
  s.addText("Cạnh trung vị của vật thể được phát hiện giảm từ 4,66% xuống 3,29% cạnh khung hình — mô hình không chỉ tìm được NHIỀU biển hơn mà còn tìm được biển NHỎ HƠN.", {
    x: 7.2, y: 4.2, w: 5.5, h: 1.1, fontFace: B, fontSize: 12.5, color: INK, margin: 0, valign: "top" });
}

// ═══════════════════ 28 · KHUNG HÌNH + PHẢN BIỆN ═══════════════════
{
  const s = lightSlide("Quan sát định tính và phản biện", "Kiểm chứng video");
  s.addImage({ path: img("video_frame_1280.jpg"), x: 0.6, y: 1.75, w: 7.0, h: 2.62 });
  s.addText("Cùng khung hình: cấu hình A cho 1 phát hiện, cấu hình B cho 8 — chênh tám lần.", {
    x: 0.6, y: 4.45, w: 7.0, h: 0.3, fontFace: B, fontSize: 12, color: GREY, italic: true, margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 4.9, w: 7.0, h: 1.35, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Chênh lệch tám lần trên một khung hình đơn lẻ", {
    x: 0.9, y: 5.08, w: 6.4, h: 0.35, fontFace: B, fontSize: 13.5, bold: true, color: NAVY, margin: 0 });
  s.addText("Mạnh hơn hẳn mức trung bình 2,6 lần của toàn bộ tập — khung hình này thuộc đúng chế độ mà mô hình yếu nhất: nhiều biển ở xa cùng lúc.", {
    x: 0.9, y: 5.45, w: 6.4, h: 0.7, fontFace: B, fontSize: 12, color: GREY, margin: 0, valign: "top" });
  s.addShape(pres.ShapeType.roundRect, { x: 7.9, y: 1.75, w: 4.8, h: 4.5, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("Phản biện: phát hiện thêm có phải nhiễu?", {
    x: 8.2, y: 1.95, w: 4.2, h: 0.65, fontFace: B, fontSize: 15, bold: true, color: AMBER, margin: 0 });
  s.addText("Cấu hình B hạ ngưỡng tin cậy từ 0,35 xuống 0,20, nên một phần phát hiện thêm CÓ THỂ là dương tính giả. Không có nhãn thật thì không loại trừ được hoàn toàn.", {
    x: 8.2, y: 2.65, w: 4.2, h: 1.0, fontFace: B, fontSize: 12, color: "DCE3EC", margin: 0, valign: "top" });
  s.addText("Hai lập luận phản bác:", { x: 8.2, y: 3.72, w: 4.2, h: 0.3, fontFace: B, fontSize: 13, bold: true, color: LIGHT, margin: 0 });
  s.addText("1 · Sàn ngưỡng hạ 15 điểm nhưng độ tin cậy trung bình chỉ giảm 5,2 điểm (0,592 → 0,540), rồi hồi lên 0,582 ở cấu hình C. Đây là lập luận YẾU hơn.\n\n2 · Lập luận chính: gradient 13,0 → 4,3 → 2,3 → 0,5 đơn điệu qua cả bốn nhóm, nhóm lớn còn GIẢM. Nhiễu ngẫu nhiên phân bố đều, không tạo ra hình dạng này.", {
    x: 8.2, y: 4.05, w: 4.2, h: 2.0, fontFace: B, fontSize: 11.5, color: "DCE3EC", margin: 0, valign: "top" });
}

// ═══════════════════ 29 · KẾT LUẬN ═══════════════════
{
  const s = lightSlide("Ba đóng góp", "Kết luận");
  numbered(s, 0.6, 1.85, 12.1, 1, "Thiết kế thực nghiệm có đối chứng đúng nghĩa",
    "Mô hình trò huấn luyện hai lần với mọi tham số giống nhau, chỉ khác việc bật/tắt chưng cất; năm ngưỡng chấp nhận khai báo trước; cơ chế xác minh kỹ thuật đã thực sự chạy.");
  numbered(s, 0.6, 3.15, 12.1, 2, "Bằng chứng định lượng: mAP tổng che giấu chi phí nén mô hình",
    "Cấu hình “giảm 70% dung lượng, mất 0,4% mAP” thực chất mất 2,47 điểm ở nhóm vật thể nhỏ — gấp 6,5 lần. Đứng vững qua hai phép kiểm chứng độc lập: trên tập sạch tỉ số TĂNG lên 2,66×, và trên video ngoài phân bố cho cùng dạng kết quả.");
  numbered(s, 0.6, 4.45, 12.1, 3, "Hai vấn đề của một bộ dữ liệu công khai đang dùng rộng rãi",
    "38,68% số ảnh là ảnh cắt cận cảnh kiểu GTSRB khiến phân bố kích thước lưỡng cực; 10,2% tập kiểm tra có bản sao trong tập huấn luyện — và 71,3% phần rò rỉ rơi đúng vào nhóm vật thể nhỏ.");
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 5.65, w: 12.1, h: 0.85, fill: { color: AMBER }, rectRadius: 0.08, line: { color: AMBER } });
  s.addText("Kiến nghị: mọi báo cáo về nén mô hình cho bài toán phát hiện nên kèm AP tách theo nhóm kích thước — chi phí bổ sung gần như bằng không nếu đã dùng bộ đánh giá COCO.", {
    x: 0.95, y: 5.83, w: 11.5, h: 0.5, fontFace: B, fontSize: 13.5, bold: true, color: NAVY, margin: 0 });
}

// ═══════════════════ 30 · HẠN CHẾ & HƯỚNG PHÁT TRIỂN ═══════════════════
{
  const s = lightSlide("Hạn chế và hướng phát triển", "Kết luận");
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 1.85, w: 5.9, h: 2.95, fill: { color: TINT }, rectRadius: 0.08, line: { color: TINT } });
  s.addText("Hạn chế", { x: 0.95, y: 2.05, w: 5.2, h: 0.38, fontFace: H, fontSize: 20, bold: true, color: RED, margin: 0 });
  bullets(s, 0.95, 2.5, 5.2, 2.3, [
    "Kích thước lô không đồng nhất giữa hai nhánh học trò (8 so với 24)",
    "Hệ số chưng cất 6,0 chưa được quét thử",
    "Phép so sánh INT8 ↔ FP32 chưa tái lập độc lập được — khác với phần chưng cất",
    "Chỉ khảo sát một cặp thầy–trò duy nhất",
    "Lượng tử hoá chỉ đo trên một môi trường thực thi",
    "Video kiểm chứng chưa có nhãn thật",
  ], 12.5);
  s.addShape(pres.ShapeType.roundRect, { x: 6.8, y: 1.85, w: 5.9, h: 2.95, fill: { color: NAVY }, rectRadius: 0.08, line: { color: NAVY } });
  s.addText("Hướng phát triển", { x: 7.15, y: 2.05, w: 5.2, h: 0.38, fontFace: H, fontSize: 20, bold: true, color: AMBER, margin: 0 });
  s.addText(
    ["Tái lập phép đo ONNX FP32 và INT8 trong cùng một môi trường thực thi",
     "Chạy lại nhánh chưng cất với lô hiệu dụng bằng 24 (tích luỹ gradient)",
     "Quét hệ số chưng cất và mở rộng khoảng cách thầy–trò",
     "Gán nhãn vài trăm khung hình video để đo AP thật ngoài phân bố",
     "Bổ sung đầu dự đoán P2 ở bước sải 4 cho vật thể nhỏ",
     "Bổ sung dữ liệu đúng miền: TT100K, Mapillary Traffic Sign"]
      .map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i !== a.length - 1 } })),
    { x: 7.15, y: 2.5, w: 5.2, h: 2.3, fontFace: B, fontSize: 12.5, color: "DCE3EC", paraSpaceAfter: 8, margin: 0, valign: "top" }
  );
}

// ═══════════════════ 31 · KẾT ═══════════════════
{
  const s = darkSlide();
  s.addText("Cảm ơn thầy cô đã lắng nghe", {
    x: 0.9, y: 2.6, w: 11.5, h: 0.85, fontFace: H, fontSize: 36, bold: true, color: LIGHT, margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 0.9, y: 3.75, w: 8.2, h: 1.0, fill: { color: NAVY_2 }, rectRadius: 0.08, line: { color: NAVY_2 } });
  s.addText("Nếu chỉ nhớ một điều: chi phí của việc nén mô hình dồn vào vật thể nhỏ — gấp 6,5 lần mức mà mAP tổng cho thấy.", {
    x: 1.15, y: 3.92, w: 7.7, h: 0.7, fontFace: B, fontSize: 14, italic: true, color: AMBER, margin: 0 });
  s.addText("Huỳnh Phát Lợi  ·  KHMT836016", {
    x: 0.9, y: 5.1, w: 8, h: 0.35, fontFace: B, fontSize: 14, color: "9FB0C4", margin: 0 });
}

fs.mkdirSync(path.dirname(OUT), { recursive: true });
pres.writeFile({ fileName: OUT }).then(() => console.log("đã ghi " + OUT + "  (" + n + " slide đánh số + 5 slide bìa/mục)"));
