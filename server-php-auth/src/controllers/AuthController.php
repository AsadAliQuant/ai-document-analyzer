<?php
require_once __DIR__ . '/../util.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/../jwt.php';
require_once __DIR__ . '/../repositories/UserRepository.php';
require_once __DIR__ . '/../RefreshTokenRepository.php';

class AuthController {
  private static function issueTokens(array $user): array {
    $cfg = app_config();
    $now = time();
    $payload = [
      'iss' => $cfg['jwt']['issuer'] ?? 'ai-auth-api',
      'sub' => (int)$user['id'],
      'email' => $user['email'],
      'role' => $user['role'],
      'iat' => $now,
      'exp' => $now + ($cfg['jwt']['access_ttl_seconds'] ?? 900)
    ];
    $access = jwt_encode($payload, $cfg['jwt']['secret']);

    $refreshPlain = rtrim(strtr(base64_encode(random_bytes(32)), '+/', '-_'), '=');
    RefreshTokenRepository::create((int)$user['id'], $refreshPlain, (int)($cfg['refresh_ttl_seconds'] ?? 2592000));

    return [
      'access_token' => $access,
      'access_expires_in' => $payload['exp'] - $now,
      'refresh_token' => $refreshPlain,
      'user' => [
        'id' => (int)$user['id'],
        'email' => $user['email'],
        'name' => $user['name'],
        'role' => $user['role'],
        'status' => $user['status']
      ]
    ];
  }

  public static function login() {
    $data = read_json();
    require_fields($data, ['email','password']);
    $user = UserRepository::verify($data['email'], $data['password']);
    if (!$user) { json_response(['error' => 'Invalid credentials'], 401); return; }
    if ($user['status'] !== 'active') { json_response(['error' => 'User disabled'], 403); return; }
    UserRepository::updateLastLogin((int)$user['id']);
    json_response(self::issueTokens($user));
  }

  public static function refresh() {
    $data = read_json();
    require_fields($data, ['refresh_token']);
    // Look up refresh token globally (by hash) and ensure not expired
    $rt = RefreshTokenRepository::findValidByPlainGlobal($data['refresh_token']);
    if (!$rt) { json_response(['error' => 'Invalid or expired refresh token'], 401); return; }
    $user = UserRepository::findById((int)$rt['user_id']);
    if (!$user || $user['status'] !== 'active') { json_response(['error' => 'User not active'], 403); return; }
    json_response(self::issueTokens($user));
  }

  public static function logout() {
    $data = read_json();
    if (isset($data['all']) && $data['all'] === true) {
      $user = require_auth();
      RefreshTokenRepository::revokeAllForUser((int)$user['id']);
      json_response(['ok' => true]);
      return;
    }
    require_fields($data, ['refresh_token']);
    $user = require_auth();
    RefreshTokenRepository::revokeByPlain((int)$user['id'], $data['refresh_token']);
    json_response(['ok' => true]);
  }

  public static function me() {
    $user = require_auth();
    json_response([
      'id' => (int)$user['id'],
      'email' => $user['email'],
      'name' => $user['name'],
      'role' => $user['role'],
      'status' => $user['status'],
      'created_at' => $user['created_at'],
      'last_login' => $user['last_login']
    ]);
  }
}
