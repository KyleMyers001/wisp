// SPDX-FileCopyrightText: 2026 Kyle Myers
//
// SPDX-License-Identifier: AGPL-3.0-or-later

import 'dart:io';

import 'package:fluffychat/config/setting_keys.dart';
import 'package:fluffychat/utils/session_backup_key.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test(
    'existing FluffyChat backup key survives the Wisp display name',
    () async {
      SharedPreferences.setMockInitialValues({});
      await AppSettings.init(loadWebConfigFile: false);

      const clientName = 'FluffyChat android';
      const legacyKey = 'FluffyChat_session_backup_FluffyChat android';
      expect(AppSettings.applicationName.value, 'Wisp');
      expect(sessionBackupKey(clientName), legacyKey);

      await AppSettings.applicationName.setItem('FluffyChat');
      expect(sessionBackupKey(clientName), legacyKey);
      await AppSettings.applicationName.setItem('Wisp');
      expect(sessionBackupKey(clientName), legacyKey);
    },
  );

  test('backup keys preserve distinct client names verbatim', () {
    const clientNames = [
      '',
      'FluffyChat android',
      'Wisp android',
      'account',
      'Account',
      ' account ',
      '@alice:example.org/device_1',
      '客户端 🐈',
    ];
    final keys = clientNames.map(sessionBackupKey).toList();

    for (var i = 0; i < clientNames.length; i++) {
      expect(keys[i], 'FluffyChat_session_backup_${clientNames[i]}');
    }
    expect(keys.toSet(), hasLength(clientNames.length));
  });

  test(
    'Wisp restore, write and logout share a display-independent backup key',
    () {
      final source = File(
        'lib/utils/init_with_restore.dart',
      ).readAsStringSync();
      final logoutSource = File('lib/widgets/matrix.dart').readAsStringSync();

      expect(source, isNot(contains('AppSettings.applicationName')));
      expect(
        source,
        contains('final storageKey = sessionBackupKey(clientName);'),
      );
      expect(source, contains('storage?.read(key: storageKey)'));
      expect(source, matches(r'storage\?\.write\(\s*key: storageKey,'));
      expect(
        source,
        matches(r'storage\?\.delete\(\s*key: sessionBackupKey\(clientName\)'),
      );
      expect(
        logoutSource,
        contains('InitWithRestoreExtension.deleteSessionBackup(name);'),
      );
    },
  );
}
