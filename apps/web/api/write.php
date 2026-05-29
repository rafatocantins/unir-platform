<?php
/**
 * Endpoint para escrever assinaturas na Google Sheet UNIR.
 * 
 * Como usar:
 * 1. Ativar Google Sheets API no Google Cloud Console
 * 2. Criar Service Account e partilhar a Sheet com o email da service account
 * 3. Guardar o JSON da chave em service-account.json
 * 
 * Este ficheiro deve ficar PROTEGIDO (.htaccess ou nginx) para só aceitar
 * pedidos do próprio domínio.
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://rafatocantins.github.io');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método não permitido']);
    exit;
}

// Ler input
$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'JSON inválido']);
    exit;
}

// Validar campos obrigatórios
$required = ['nome', 'email', 'cc', 'nascimento', 'postal', 'morada'];
foreach ($required as $field) {
    if (empty($input[$field])) {
        http_response_code(400);
        echo json_encode(['error' => "Campo obrigatório: $field"]);
        exit;
    }
}

// ID da Google Sheet
$sheetId = '1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20';

// Caminho da service account
$serviceAccountPath = __DIR__ . '/service-account.json';

require_once __DIR__ . '/vendor/autoload.php';

putenv("GOOGLE_APPLICATION_CREDENTIALS=$serviceAccountPath");

$client = new Google_Client();
$client->useApplicationDefaultCredentials();
$client->addScope(Google_Service_Sheets::SPREADSHEETS);

$service = new Google_Service_Sheets($client);

$row = [
    date('Y-m-d H:i:s'),
    $input['nome'],
    $input['email'],
    $input['cc'],
    $input['nascimento'],
    $input['postal'],
    $input['morada'],
    'Sim',
    $input['quota'] ?? '0',
    $input['interesses'] ?? '',
    'Pendente',
    'Recolhida',
    ''
];

$body = new Google_Service_Sheets_ValueRange([
    'values' => [$row]
]);

try {
    $result = $service->spreadsheets_values->append(
        $sheetId,
        'A2:M',
        $body,
        ['valueInputOption' => 'RAW', 'insertDataOption' => 'INSERT_ROWS']
    );
    
    http_response_code(200);
    echo json_encode([
        'success' => true,
        'message' => 'Assinatura registada com sucesso'
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Erro ao registar assinatura: ' . $e->getMessage()
    ]);
}
