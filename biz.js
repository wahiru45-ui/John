// 사업자 정보 (전자상거래법 표시 사항) — 바꿀 때는 이 파일만 고치면 모든 손님 화면에 반영돼요
(function () {
  var BIZ = {
    name: "더 맛있는 밥집",
    ceo: "민형준",
    regNo: "472-54-00945",
    addr: "광주광역시 서구 계수로59번길 4, 1층 (쌍촌동)",
    tel: "062-385-3450",
    mailOrder: ""          // 통신판매업 신고번호 (신고 후 입력)
  };
  function draw() {
    if (document.getElementById("bizFooter")) return;
    var f = document.createElement("footer");
    f.id = "bizFooter";
    f.style.cssText = "margin:24px 0 0;padding:16px 16px 96px;font-size:11.5px;line-height:1.7;color:#888;border-top:1px solid #e5e5e5;text-align:left;word-break:keep-all;background:transparent";
    f.innerHTML =
      "<b style='color:#666'>" + BIZ.name + "</b><br>" +
      "대표자 " + BIZ.ceo + " · 사업자등록번호 " + BIZ.regNo +
      " <a href='https://www.ftc.go.kr/bizCommPop.do?wrkr_no=" + BIZ.regNo.replace(/-/g, "") + "' target='_blank' rel='noopener' style='color:#999'>[사업자정보확인]</a><br>" +
      (BIZ.mailOrder ? "통신판매업 신고번호 " + BIZ.mailOrder + "<br>" : "") +
      "주소 " + BIZ.addr + "<br>" +
      "전화 <a href='tel:" + BIZ.tel.replace(/-/g, "") + "' style='color:#888'>" + BIZ.tel + "</a>";
    document.body.appendChild(f);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", draw); else draw();
  window.BIZ = BIZ;
})();
