[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "در حال بروزرسانی و تحلیل عمیق ساختار پروژه..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# 1. بروزرسانی کامل گراف پروژه
graphify update .

Write-Host "`nبروزرسانی کامل شد." -ForegroundColor Yellow
$query = Read-Host "موضوع یا تغییر کد مورد نظر را وارد کنید"

if ($query) {
    Write-Host "`nدر حال اجرای جستجوی عمیق..." -ForegroundColor Green
    graphify query "$query" --dfs --context 5 --budget 50000
} else {
    Write-Host "`nهیچ عبارتی وارد نشد." -ForegroundColor Red
}

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "عملیات پایان یافت. برای خروج یک کلید را فشار دهید..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")