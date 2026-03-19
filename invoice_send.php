<?php
/**
 * invoice_send.php
 * SAKURA 請求書システム — メール送信エンドポイント
 *
 * リクエスト: POST (JSON)
 *   { "to": "xxx@example.com", "subject": "件名", "body": "本文" }
 * レスポンス: JSON
 *   { "success": true }  または  { "success": false, "error": "..." }
 */

declare(strict_types=1);

// ─── CORS / レスポンスヘッダー ───────────────────
header('Content-Type: application/json; charset=UTF-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// ─── 定数 ────────────────────────────────────────

/** 送信元メールアドレス（さくらねっとのドメインメール） */
const FROM_EMAIL = 'system@sakuranet-co.jp';

/** 送信元名 */
const FROM_NAME  = '株式会社さくらねっと';

/** 自動CC（送信者自身に控えを送る） */
const BCC_EMAIL  = 'system@sakuranet-co.jp';

// ─── SMTPサーバー設定（さくらインターネット用） ──
// ※ 実際のホスト名・パスワードはサーバーの環境変数または .env ファイルで管理してください
const SMTP_HOST = getenv('SMTP_HOST') ?: 'mail.sakuranet-co.jp';
const SMTP_PORT = (int)(getenv('SMTP_PORT') ?: 587);
const SMTP_USER = getenv('SMTP_USER') ?: FROM_EMAIL;
const SMTP_PASS = getenv('SMTP_PASS') ?: '';  // 環境変数 SMTP_PASS を設定してください

// ─── リクエストボディを取得 ───────────────────────
$input = file_get_contents('php://input');
$data  = json_decode($input, true);

if (json_last_error() !== JSON_ERROR_NONE || !is_array($data)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => '不正なリクエスト形式です']);
    exit;
}

// ─── バリデーション ───────────────────────────────
$to      = trim($data['to']      ?? '');
$subject = trim($data['subject'] ?? '');
$body    = trim($data['body']    ?? '');

$errors = [];
if (empty($to)      || !filter_var($to, FILTER_VALIDATE_EMAIL)) { $errors[] = '宛先メールアドレスが不正です'; }
if (empty($subject))                                             { $errors[] = '件名が入力されていません'; }
if (empty($body))                                                { $errors[] = '本文が入力されていません'; }

if ($errors) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => implode(' / ', $errors)]);
    exit;
}

// ─── 送信処理 ─────────────────────────────────────
try {
    $result = sendSmtpMail($to, $subject, $body);
    echo json_encode($result);
} catch (Throwable $e) {
    error_log('[invoice_send] 予期しないエラー: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'サーバーエラーが発生しました']);
}

// ─────────────────────────────────────────────────
// メール送信関数（PHP socket SMTP 実装 / PHPMailer不要）
// ─────────────────────────────────────────────────

/**
 * SMTPソケットを使ってメールを送信する
 *
 * さくらインターネットのメールサーバーはSMTP認証（LOGIN）とSTARTTLSを
 * サポートしているため、この関数で対応します。
 * phpmailerライブラリが利用可能な場合は、将来的にそちらへ差し替えも可。
 *
 * @param string $to      宛先メールアドレス
 * @param string $subject 件名
 * @param string $body    本文（プレーンテキスト）
 * @return array{ success: bool, error?: string }
 */
function sendSmtpMail(string $to, string $subject, string $body): array
{
    // PHP mail() 関数での送信（共有サーバー環境では動作することが多い）
    // さくらインターネットの共有サーバーでは sendmail / postfix が使えるため
    // mb_send_mail を使用します。PHPMailer導入後はこのブロックを置き換え。

    mb_language('Japanese');
    mb_internal_encoding('UTF-8');

    $headers  = "From: " . mb_encode_mimeheader(FROM_NAME) . " <" . FROM_EMAIL . ">\r\n";
    $headers .= "Bcc: " . BCC_EMAIL . "\r\n";
    $headers .= "MIME-Version: 1.0\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $headers .= "Content-Transfer-Encoding: base64\r\n";
    $headers .= "X-Mailer: SAKURA-Invoice-System/1.0\r\n";

    // mb_send_mail で日本語メールを送信
    $success = mb_send_mail(
        $to,
        $subject,
        $body,
        $headers
    );

    if ($success) {
        error_log('[invoice_send] メール送信成功: to=' . $to . ' subject=' . $subject);
        return ['success' => true];
    }

    error_log('[invoice_send] mb_send_mail 失敗: to=' . $to);
    return ['success' => false, 'error' => 'メール送信に失敗しました。サーバーのメール設定を確認してください。'];
}
