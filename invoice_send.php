<?php
/**
 * invoice_send.php
 * SAKURA 請求書システム — メール送信エンドポイント（PDF添付対応）
 *
 * リクエスト: POST (JSON)
 *   {
 *     "to": "xxx@example.com",
 *     "subject": "件名",
 *     "body": "本文",
 *     "pdf_base64": "JVBERi...",   // base64エンコードされたPDF（省略可）
 *     "pdf_filename": "請求書_202603_001.pdf"  // 添付ファイル名（省略可）
 *   }
 */

declare(strict_types=1);

header('Content-Type: application/json; charset=UTF-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

const FROM_EMAIL = 'system@sakuranet-co.jp';
const FROM_NAME  = '株式会社さくらねっと';
const BCC_EMAIL  = 'system@sakuranet-co.jp';

$input = file_get_contents('php://input');
$data  = json_decode($input, true);

if (json_last_error() !== JSON_ERROR_NONE || !is_array($data)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => '不正なリクエスト形式です']);
    exit;
}

$toRaw   = trim($data['to']      ?? '');
$subject = trim($data['subject'] ?? '');
$body    = trim($data['body']    ?? '');

// 宛先：カンマ区切り複数アドレスを解析
$toAddrs = array_values(array_filter(array_map('trim', explode(',', $toRaw))));

// pdfs 配列（複数添付）
$pdfs = [];
if (!empty($data['pdfs']) && is_array($data['pdfs'])) {
    foreach ($data['pdfs'] as $p) {
        $b64  = trim($p['pdf_base64']  ?? '');
        $name = trim($p['pdf_filename'] ?? '請求書.pdf');
        if (!empty($b64)) {
            $pdfs[] = ['base64' => $b64, 'filename' => $name];
        }
    }
}

$errors = [];
if (empty($toAddrs)) {
    $errors[] = '宛先メールアドレスが入力されていません';
} else {
    foreach ($toAddrs as $addr) {
        if (!filter_var($addr, FILTER_VALIDATE_EMAIL)) {
            $errors[] = "宛先メールアドレスが不正です: {$addr}";
        }
    }
}
if (empty($subject)) { $errors[] = '件名が入力されていません'; }
if (empty($body))    { $errors[] = '本文が入力されていません'; }

if ($errors) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => implode(' / ', $errors)]);
    exit;
}

try {
    $result = sendMailWithAttachments($toAddrs, $subject, $body, $pdfs);
    echo json_encode($result);
} catch (Throwable $e) {
    error_log('[invoice_send] 予期しないエラー: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'サーバーエラーが発生しました']);
}

function sendMailWithAttachments(
    array  $toAddrs,
    string $subject,
    string $body,
    array  $pdfs
): array {
    mb_language('Japanese');
    mb_internal_encoding('UTF-8');

    // 複数宛先をカンマ結合
    $to = implode(', ', $toAddrs);

    $boundary = '----=_Part_' . md5(uniqid((string)mt_rand(), true));

    if (empty($pdfs)) {
        // PDF添付なし: プレーンテキストメール
        $headers  = "From: " . mb_encode_mimeheader(FROM_NAME) . " <" . FROM_EMAIL . ">\r\n";
        $headers .= "Cc: " . FROM_EMAIL . "\r\n";
        $headers .= "Bcc: " . BCC_EMAIL . "\r\n";
        $headers .= "MIME-Version: 1.0\r\n";
        $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
        $headers .= "Content-Transfer-Encoding: base64\r\n";

        $success = mb_send_mail($to, $subject, $body, $headers);
    } else {
        // PDF添付あり: multipart/mixed（複数対応）
        $headers  = "From: " . mb_encode_mimeheader(FROM_NAME) . " <" . FROM_EMAIL . ">\r\n";
        $headers .= "Cc: " . FROM_EMAIL . "\r\n";
        $headers .= "Bcc: " . BCC_EMAIL . "\r\n";
        $headers .= "MIME-Version: 1.0\r\n";
        $headers .= "Content-Type: multipart/mixed; boundary=\"{$boundary}\"\r\n";

        // 本文パート
        $encodedBody = base64_encode($body);
        $bodyChunked = chunk_split($encodedBody, 76, "\r\n");

        $messageBody  = "--{$boundary}\r\n";
        $messageBody .= "Content-Type: text/plain; charset=UTF-8\r\n";
        $messageBody .= "Content-Transfer-Encoding: base64\r\n\r\n";
        $messageBody .= $bodyChunked . "\r\n";

        // PDFパート（複数）
        foreach ($pdfs as $pdf) {
            $pdfChunked      = chunk_split($pdf['base64'], 76, "\r\n");
            $encodedFilename = mb_encode_mimeheader($pdf['filename'], 'UTF-8', 'B');

            $messageBody .= "--{$boundary}\r\n";
            $messageBody .= "Content-Type: application/pdf; name=\"{$encodedFilename}\"\r\n";
            $messageBody .= "Content-Transfer-Encoding: base64\r\n";
            $messageBody .= "Content-Disposition: attachment; filename=\"{$encodedFilename}\"\r\n\r\n";
            $messageBody .= $pdfChunked . "\r\n";
        }

        $messageBody .= "--{$boundary}--\r\n";

        $success = mb_send_mail($to, $subject, $messageBody, $headers);
    }

    if ($success) {
        error_log('[invoice_send] 送信成功: to=' . $to . ' pdfs=' . count($pdfs));
        return ['success' => true];
    }

    error_log('[invoice_send] mb_send_mail 失敗: to=' . $to);
    return ['success' => false, 'error' => 'メール送信に失敗しました。サーバーのメール設定を確認してください。'];
}
