import os
import re
import sys

def patch_werygram_core():
    settings_path = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
    userconfig_path = "TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
    messages_path = "TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    
    if not os.path.exists(settings_path):
        print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: Файл не найден: {settings_path}")
        sys.exit(1)

    print("⏳ Тройной авто-патчер WeryGram Premium запущен...")

    # ==========================================
    # 1. МОДЕРНИЗАЦИЯ ИНТЕРФЕЙСА (SettingsActivity)
    # ==========================================
    with open(settings_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Очищаем старые версии кнопки и кейсов
    code = re.sub(r'case 9999:.*?break;', '', code, flags=re.DOTALL)
    code = re.sub(r'items\.add\(SettingCell\.Factory\.of\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'items\.add\(UItem\.asCheck\(9999,[\s\S]*?\);\s*', '', code)

    # Создаем кнопку-тумблер (CheckCell), которая читает настройки из глобального конфига
    werygram_toggle = 'items.add(UItem.asCheck(9999, "WeryGram Premium").setChecked(org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)));'

    # Ставим кнопку в САМЫЙ ВЕРХ первого списка (прямо перед Уведомлениями / Notifications)
    match_notif = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)
    if match_notif:
        anchor = match_notif.group(1)
        code = code.replace(anchor, f'{werygram_toggle}\n        {anchor}')
        print("✅ Кнопка-тумблер WeryGram установлена на самый верх первого списка!")
    else:
        code = code.replace("switch (item.id) {", "items.add(0, UItem.asCheck(9999, \"WeryGram Premium\"));\n        switch (item.id) {")
        print("✅ Кнопка-тумблер WeryGram установлена в начало списка (резервный метод).")

    # Вшиваем обработку клика: переключение тумблера + моментальное уведомление (Toast)
    switch_anchor = "switch (item.id) {"
    if switch_anchor in code:
        # ИСПРАВЛЕНО: Безопасное обновление элемента через родительский RecyclerView
        click_logic = """case 9999: {
            boolean newState = !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false);
            org.telegram.messenger.MessagesController.getGlobalMainSettings().edit().putBoolean("visual_premium", newState).apply();
            
            item.checked = newState;
            if (view instanceof org.telegram.ui.Cells.TextCheckCell) {
                ((org.telegram.ui.Cells.TextCheckCell) view).setChecked(newState);
            }
            
            android.widget.Toast.makeText(SettingsActivity.this.getParentActivity(), newState ? "WeryGram: Visual Premium АКТИВИРОВАН! 🎉" : "WeryGram: Visual Premium ОТКЛЮЧЕН", android.widget.Toast.LENGTH_SHORT).show();
            
            // Мгновенно обновляем наш профиль на экране
            org.telegram.messenger.UserConfig.getInstance(currentAccount).getCurrentUser();
            if (view != null && view.getParent() instanceof androidx.recyclerview.widget.RecyclerView) {
                androidx.recyclerview.widget.RecyclerView.Adapter adapter = ((androidx.recyclerview.widget.RecyclerView) view.getParent()).getAdapter();
                if (adapter != null) {
                    adapter.notifyItemChanged(position);
                }
            }
            break;
        }"""
        code = code.replace(switch_anchor, f"{switch_anchor}\n            {click_logic}")
        print("✅ Быстрый переключатель с уведомлением успешно добавлен в клики!")

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(code)

    # ==========================================
    # 2. АКТИВАЦИЯ ПРЕМИУМА В СИСТЕМЕ (UserConfig)
    # ==========================================
    if os.path.exists(userconfig_path):
        with open(userconfig_path, "r", encoding="utf-8") as f:
            uc_code = f.read()
        
        if "visual_premium" not in uc_code:
            uc_anchor = "public TLRPC.User getCurrentUser() {"
            if uc_anchor in uc_code:
                uc_injection = """public TLRPC.User getCurrentUser() {
        if (currentUser != null && org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
            currentUser.premium = true;
            currentUser.verified = true;
        }"""
                uc_code = uc_code.replace(uc_anchor, uc_injection)
                with open(userconfig_path, "w", encoding="utf-8") as f:
                    f.write(uc_code)
                print("✅ Логика Premium + Галочка успешно внедрены в профиль аккаунта!")

    # ==========================================
    # 3. ПОДМЕНА СТАТУСА ДЛЯ ОТОБРАЖЕНИЯ (MessagesController)
    # ==========================================
    if os.path.exists(messages_path):
        with open(messages_path, "r", encoding="utf-8") as f:
            mc_code = f.read()
        
        if "visual_premium" not in mc_code:
            mc_code = re.sub(
                r'public TLRPC\.User getUser\((Long|Integer)\s+(\w+)\)\s*\{\s*return\s+(\w+)\.get\(\2\);\s*\}',
                r'''public TLRPC.User getUser(\1 \2) {
        TLRPC.User user = \3.get(\2);
        if (user != null && \2 != null && \2.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
                user.premium = true;
                user.verified = true;
            }
        }
        return user;
    }''',
                mc_code
            )
            with open(messages_path, "w", encoding="utf-8") as f:
                f.write(mc_code)
            print("✅ Системный перехватчик ID запущен. Статус Premium активен глобально!")

    print("\n🎉 ВСЕ МОДУЛИ УСПЕШНО МОДИФИЦИРОВАНЫ! Проект готов к полной сборке.")

if __name__ == "__main__":
    patch_werygram_core()
