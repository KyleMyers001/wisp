// SPDX-FileCopyrightText: 2026 Kyle Myers
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Keep the original secure-storage namespace independent of display branding.
String sessionBackupKey(String clientName) =>
    'FluffyChat_session_backup_$clientName';
