<?php
// Resolve src path for both deployments where index.php is under /public or root
$srcA = __DIR__ . '/../src';
$srcB = __DIR__ . '/src';
$SRC = is_dir($srcA) ? $srcA : $srcB;

require_once $SRC . '/util.php';
require_once $SRC . '/db.php';
require_once $SRC . '/jwt.php';
require_once $SRC . '/auth.php';
require_once $SRC . '/repositories/UserRepository.php';
require_once $SRC . '/RefreshTokenRepository.php';
require_once $SRC . '/controllers/AuthController.php';
require_once $SRC . '/controllers/AdminController.php';

$method = $_SERVER['REQUEST_METHOD'];
$uriPath = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$base = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/');
$route = '/' . ltrim(substr($uriPath, strlen($base)), '/');

if ($route === '/health' && $method === 'GET') {
  json_response(['status' => 'ok']);
  exit;
}

if ($route === '/login' && $method === 'POST') { AuthController::login(); exit; }
if ($route === '/token/refresh' && $method === 'POST') { AuthController::refresh(); exit; }
if ($route === '/logout' && $method === 'POST') { AuthController::logout(); exit; }
if ($route === '/me' && $method === 'GET') { AuthController::me(); exit; }

if ($route === '/register') { json_response(['error' => 'Registration disabled'], 403); exit; }

if ($route === '/admin/users' && $method === 'GET') { AdminController::listUsers(); exit; }
if ($route === '/admin/users' && $method === 'POST') { AdminController::createUser(); exit; }
if (preg_match('#^/admin/users/(\d+)/reset-password$#', $route, $m) && $method === 'POST') { $_GET['id'] = (int)$m[1]; AdminController::resetPassword(); exit; }
if (preg_match('#^/admin/users/(\d+)/status$#', $route, $m) && $method === 'POST') { $_GET['id'] = (int)$m[1]; AdminController::updateStatus(); exit; }

http_response_code(404);
json_response(['error' => 'Not found'], 404);
