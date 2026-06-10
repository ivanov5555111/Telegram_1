#!/usr/bin/env python3
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "TMessagesProj", "src", "main", "java")

def find_file(name):
    for dp, _, files in os.walk(SRC):
        if name in files:
            return os.path.join(dp, name)
    return None

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def write(p, t):
    with open(p, "w", encoding="utf-8") as f: f.write(t)
    print(f"✔ {os.path.relpath(p, ROOT)}")

def find_method_end(text, open_brace):
    depth = 0
    i = open_brace
    while i < len(text):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return len(text) - 1

def insert_before(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text:
        print(f"↩ skip {os.path.relpath(path, ROOT)}"); return True
    if marker not in text:
        print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, insertion + "\n" + marker, 1)); return True

def insert_after(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text:
        print(f"↩ skip {os.path.relpath(path, ROOT)}"); return True
    if marker not in text:
        print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, marker + "\n" + insertion, 1)); return True

ACTIVITY = '''\
package org.telegram.ui;
import android.content.Context;
import android.content.SharedPreferences;
import android.widget.LinearLayout;
import android.widget.Switch;
import android.widget.TextView;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.NotificationCenter;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;
public class WeryGramPremiumActivity extends BaseFragment {
    private SharedPreferences prefs;
    private void addRow(Context ctx, LinearLayout parent, String title, String sub, String key) {
        LinearLayout row = new LinearLayout(ctx);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(AndroidUtilities.dp(16), AndroidUtilities.dp(14), AndroidUtilities.dp(16), AndroidUtilities.dp(14));
        row.setGravity(android.view.Gravity.CENTER_VERTICAL);
        LinearLayout labels = new LinearLayout(ctx);
        labels.setOrientation(LinearLayout.VERTICAL);
        labels.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        TextView t = new TextView(ctx);
        t.setText(title);
        t.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 16);
        t.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        TextView s = new TextView(ctx);
        s.setText(sub);
        s.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 13);
        s.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteGrayText2));
        labels.addView(t);
        labels.addView(s);
        android.view.View div = new android.view.View(ctx);
        div.setBackgroundColor(Theme.getColor(Theme.key_divider));
        LinearLayout.LayoutParams dp2 = new LinearLayout.LayoutParams(AndroidUtilities.dp(1), AndroidUtilities.dp(40));
        dp2.setMargins(AndroidUtilities.dp(12), 0, AndroidUtilities.dp(12), 0);
        div.setLayoutParams(dp2);
        Switch toggle = new Switch(ctx);
        toggle.setChecked(prefs.getBoolean(key, false));
        toggle.setOnCheckedChangeListener((btn, checked) -> {
            prefs.edit().putBoolean(key, checked).apply();
            NotificationCenter.getGlobalInstance().postNotificationName(NotificationCenter.currentUserPremiumStatusChanged);
        });
        row.addView(labels);
        row.addView(div);
        row.addView(toggle);
        parent.addView(row);
        android.view.View divider = new android.view.View(ctx);
        divider.setBackgroundColor(Theme.getColor(Theme.key_divider));
        divider.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1));
        parent.addView(divider);
    }
    @Override
    public android.view.View createView(Context context) {
        actionBar.setBackButtonImage(org.telegram.messenger.R.drawable.ic_ab_back);
        actionBar.setTitle("WeryGram");
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override public void onItemClick(int id) { if (id == -1) finishFragment(); }
        });
        prefs = MessagesController.getGlobalMainSettings();
        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        addRow(context, root,
            "Visual Premium",
            "\u0414\u0430\u0451\u0442 \u0432\u0438\u0437\u0443\u0430\u043b\u044c\u043d\u043e Telegram Premium",
            "wery_visual_premium");
        addRow(context, root,
            "\u0420\u0435\u0436\u0438\u043c \u041f\u0440\u0438\u0437\u0440\u0430\u043a\u0430",
            "\u0412\u044b \u0431\u0443\u0434\u0435\u0442\u0435 \u0432 \u0441\u0442\u0430\u0442\u0443\u0441\u0435 \u043d\u0435\u0432\u0438\u0434\u0438\u043c\u043a\u0438, \u0430 \u0442\u0430\u043a\u0436\u0435 \u043f\u0440\u0438 \u043f\u0440\u043e\u0447\u0442\u0435\u043d\u0438\u0438 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440 \u043d\u0435 \u0431\u0443\u0434\u0435\u0442 \u0437\u0430\u0441\u0447\u0438\u0442\u044b\u0432\u0430\u0442\u044c\u0441\u044f",
            "wery_ghost_mode");
        addRow(context, root,
            "\u0423\u0434\u0430\u043b\u0451\u043d\u043d\u044b\u0435 \u043f\u043e\u0434\u0430\u0440\u043a\u0438",
            "\u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0434\u0430\u0440\u0438\u0442\u044c \u0443\u0434\u0430\u043b\u0451\u043d\u043d\u044b\u0435 \u043f\u043e\u0434\u0430\u0440\u043a\u0438",
            "wery_deleted_gifts");
        fragmentView = root;
        return fragmentView;
    }
}
'''

def patch_user_config(errors):
    uc = find_file("UserConfig.java")
    if not uc:
        print("✘ UserConfig.java not found", file=sys.stderr)
        return errors + 1
    text = read(uc)
    if 'wery_visual_premium' in text:
        print("↩ skip UserConfig"); return errors
    sig_pos = text.find("getCurrentUser()")
    if sig_pos == -1:
        print("✘ UserConfig: getCurrentUser() не найден", file=sys.stderr)
        return errors + 1
    ret_pos = text.find("return currentUser;", sig_pos)
    if ret_pos == -1:
        print("✘ UserConfig: return currentUser; не найден", file=sys.stderr)
        return errors + 1
    line_start = text.rfind('\n', 0, ret_pos) + 1
    indent = ''
    for ch in text[line_start:ret_pos]:
        if ch in (' ', '\t'): indent += ch
        else: break
    patch = (
        f'{indent}try {{\n'
        f'{indent}    android.content.SharedPreferences __p = org.telegram.messenger.MessagesController.getGlobalMainSettings();\n'
        f'{indent}    if (currentUser != null && __p.getBoolean("wery_visual_premium", false)) {{\n'
        f'{indent}        currentUser.premium = true;\n'
        f'{indent}        if (currentUser.emoji_status instanceof org.telegram.tgnet.TLRPC.TL_emojiStatus) {{\n'
        f'{indent}            long __curEid = ((org.telegram.tgnet.TLRPC.TL_emojiStatus) currentUser.emoji_status).document_id;\n'
        f'{indent}            if (__curEid != 0) {{\n'
        f'{indent}                __p.edit().putLong("wery_emoji_id", __curEid).apply();\n'
        f'{indent}            }} else {{\n'
        f'{indent}                long __savedEid = __p.getLong("wery_emoji_id", 0);\n'
        f'{indent}                if (__savedEid != 0) ((org.telegram.tgnet.TLRPC.TL_emojiStatus) currentUser.emoji_status).document_id = __savedEid;\n'
        f'{indent}            }}\n'
        f'{indent}        }} else {{\n'
        f'{indent}            long __savedEid = __p.getLong("wery_emoji_id", 0);\n'
        f'{indent}            if (__savedEid != 0) {{\n'
        f'{indent}                org.telegram.tgnet.TLRPC.TL_emojiStatus __es = new org.telegram.tgnet.TLRPC.TL_emojiStatus();\n'
        f'{indent}                __es.document_id = __savedEid;\n'
        f'{indent}                currentUser.emoji_status = __es;\n'
        f'{indent}            }}\n'
        f'{indent}        }}\n'
        f'{indent}        if (currentUser.profile_color != null) {{\n'
        f'{indent}            int __cColor = currentUser.profile_color.color;\n'
        f'{indent}            long __cEmoji = currentUser.profile_color.background_emoji_id;\n'
        f'{indent}            if (__cColor >= 0 || __cEmoji != 0) {{\n'
        f'{indent}                __p.edit().putInt("wery_pcolor_id", __cColor).putLong("wery_pcolor_emoji", __cEmoji).apply();\n'
        f'{indent}            }} else {{\n'
        f'{indent}                int __savedPid = __p.getInt("wery_pcolor_id", -1);\n'
        f'{indent}                long __savedPEmoji = __p.getLong("wery_pcolor_emoji", 0);\n'
        f'{indent}                if (__savedPid >= 0) currentUser.profile_color.color = __savedPid;\n'
        f'{indent}                if (__savedPEmoji != 0) currentUser.profile_color.background_emoji_id = __savedPEmoji;\n'
        f'{indent}            }}\n'
        f'{indent}        }} else {{\n'
        f'{indent}            int __savedPid = __p.getInt("wery_pcolor_id", -1);\n'
        f'{indent}            long __savedPEmoji = __p.getLong("wery_pcolor_emoji", 0);\n'
        f'{indent}            if (__savedPid >= 0 || __savedPEmoji != 0) {{\n'
        f'{indent}                currentUser.profile_color = new org.telegram.tgnet.TLRPC.TL_peerColor();\n'
        f'{indent}                if (__savedPid >= 0) currentUser.profile_color.color = __savedPid;\n'
        f'{indent}                currentUser.profile_color.background_emoji_id = __savedPEmoji;\n'
        f'{indent}            }}\n'
        f'{indent}        }}\n'
        f'{indent}        if (currentUser.color != null) {{\n'
        f'{indent}            int __nColor = currentUser.color.color;\n'
        f'{indent}            long __nEmoji = currentUser.color.background_emoji_id;\n'
        f'{indent}            if (__nColor >= 0 || __nEmoji != 0) {{\n'
        f'{indent}                __p.edit().putInt("wery_color_id", __nColor).putLong("wery_color_emoji", __nEmoji).apply();\n'
        f'{indent}            }} else {{\n'
        f'{indent}                int __savedCid = __p.getInt("wery_color_id", -1);\n'
        f'{indent}                long __savedCEmoji = __p.getLong("wery_color_emoji", 0);\n'
        f'{indent}                if (__savedCid >= 0) currentUser.color.color = __savedCid;\n'
        f'{indent}                if (__savedCEmoji != 0) currentUser.color.background_emoji_id = __savedCEmoji;\n'
        f'{indent}            }}\n'
        f'{indent}        }} else {{\n'
        f'{indent}            int __savedCid = __p.getInt("wery_color_id", -1);\n'
        f'{indent}            long __savedCEmoji = __p.getLong("wery_color_emoji", 0);\n'
        f'{indent}            if (__savedCid >= 0 || __savedCEmoji != 0) {{\n'
        f'{indent}                currentUser.color = new org.telegram.tgnet.TLRPC.TL_peerColor();\n'
        f'{indent}                if (__savedCid >= 0) currentUser.color.color = __savedCid;\n'
        f'{indent}                currentUser.color.background_emoji_id = __savedCEmoji;\n'
        f'{indent}            }}\n'
        f'{indent}        }}\n'
        f'{indent}    }}\n'
        f'{indent}}} catch (Exception __e) {{}}\n'
        f'{indent}'
    )
    new_text = text[:ret_pos] + patch + text[ret_pos:]
    write(uc, new_text)
    return errors

def patch_messages_controller(errors):
    mc = find_file("MessagesController.java")
    if not mc:
        print("✘ MessagesController.java not found", file=sys.stderr)
        return errors + 1
    text = read(mc)
    modified = False

    # Premium только для себя
    if 'wery_visual_premium' not in text:
        variants = [
            "public TLRPC.User getUser(Long id) {",
            "public TLRPC.User getUser(Long uid) {",
            "public TLRPC.User getUser(Long javaLong) {",
        ]
        marker = next((v for v in variants if v in text), None)
        if marker:
            var_name = "id" if "Long id)" in marker else ("uid" if "Long uid)" in marker else "javaLong")
            insertion = (
                f"        if ({var_name} != null && !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean(\"wery_visual_premium\", false) == false\n"
                f"            && {var_name}.longValue() == UserConfig.getInstance(currentAccount).getClientUserId()) {{\n"
                f"            org.telegram.tgnet.TLRPC.User __u = users.get({var_name});\n"
                f"            if (__u != null && !__u.bot) __u.premium = true;\n"
                f"        }}"
            )
            text = text.replace(marker, marker + "\n" + insertion, 1)
            modified = True
            print("✔ MessagesController: premium patch")

    # Режим Призрака — онлайн статус
    if 'wery_ghost_online' not in text:
        online_markers = [
            "public void sendOnlineIfNeed() {",
            "void sendOnlineIfNeed() {",
            "public void sendOnline() {",
        ]
        m = next((x for x in online_markers if x in text), None)
        if m:
            text = text.replace(m,
                m + '\n        if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wery_ghost_mode", false)) return; //wery_ghost_online',
                1)
            modified = True
            print("✔ Ghost mode: online status patched")
        else:
            print("⚠ Ghost mode: sendOnlineIfNeed не найден")

    # Режим Призрака — прочтение сообщений
    if 'wery_ghost_read' not in text:
        read_markers = [
            "public void markDialogAsRead(",
            "public void readMessages(",
            "public void markMessagesAsRead(",
        ]
        m = next((x for x in read_markers if x in text), None)
        if m:
            brace_pos = text.find('{', text.find(m))
            if brace_pos != -1:
                ins = '\n        if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wery_ghost_mode", false)) return; //wery_ghost_read'
                text = text[:brace_pos+1] + ins + text[brace_pos+1:]
                modified = True
                print("✔ Ghost mode: read receipt patched")
        else:
            print("⚠ Ghost mode: read method не найден")

    # Удалённые подарки — убираем фильтр sold_out
    if 'wery_deleted_gifts' not in text:
        gift_markers = [
            "if (gift.sold_out)",
            "gift.sold_out ||",
            "|| gift.sold_out",
            ".sold_out) continue;",
            ".sold_out) return;",
        ]
        m = next((x for x in gift_markers if x in text), None)
        if m:
            text = text.replace(m,
                f'if (false && !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wery_deleted_gifts", false) && {m[3:] if m.startswith("if ") else m}',
                1)
            modified = True
            print("✔ Deleted gifts: sold_out filter patched")
        else:
            print("⚠ Deleted gifts: sold_out filter не найден")

    if modified:
        write(mc, text)
    return errors

def main():
    print("▶ WeryGram patcher\n")
    errors = 0
    errors = patch_user_config(errors)
    errors = patch_messages_controller(errors)
    sa = find_file("SettingsActivity.java")
    if not sa: print("✘ SettingsActivity.java not found", file=sys.stderr); sys.exit(1)
    if not insert_before(sa, "import org.telegram.ui.Components.", "import org.telegram.ui.WeryGramPremiumActivity;"): errors += 1
    fill_anchors = [
        "void fillItems(ArrayList<UItem> items, UniversalAdapter adapter) {",
        "public void fillItems(ArrayList<UItem> items, UniversalAdapter adapter) {",
        "private void fillItems(ArrayList<UItem> items, UniversalAdapter adapter) {",
    ]
    text = read(sa)
    fill_anchor = next((a for a in fill_anchors if a in text), None)
    if fill_anchor:
        if 'UItem.asButton(1000' not in text:
            anchor_pos = text.find(fill_anchor)
            open_brace = text.find('{', anchor_pos)
            method_end = find_method_end(text, open_brace)
            new_text = (text[:method_end] +
                '        items.add(UItem.asButton(1000, R.drawable.msg_settings, "WeryGram"));\n' +
                text[method_end:])
            write(sa, new_text)
        else:
            print("↩ skip fillItems")
    else:
        print("✘ fillItems не найден", file=sys.stderr); errors += 1
    click_anchors = [
        "void onItemClick(UItem item, View view, int position, float x, float y) {",
        "public void onItemClick(UItem item, View view, int position, float x, float y) {",
        "private void onItemClick(UItem item, View view, int position, float x, float y) {",
        "private void onClick(UItem item, View view, int position, float x, float y) {",
        "void onClick(UItem item, View view, int position, float x, float y) {",
        "public void onClick(UItem item, View view, int position, float x, float y) {",
        "void onClick(UItem item) {",
        "public void onClick(UItem item) {",
    ]
    click_anchor = next((a for a in click_anchors if a in read(sa)), None)
    if click_anchor:
        if not insert_after(sa, click_anchor,
            '        if (item.id == 1000) { presentFragment(new WeryGramPremiumActivity()); return; }'):
            errors += 1
    else:
        print("✘ onClick не найден", file=sys.stderr); errors += 1
    dest = os.path.join(os.path.dirname(sa), "WeryGramPremiumActivity.java")
    if os.path.exists(dest): os.remove(dest)
    with open(dest, "w", encoding="utf-8") as f: f.write(ACTIVITY)
    print("✔ created WeryGramPremiumActivity.java")
    if errors > 0:
        print(f"\n✘ {errors} ошибок", file=sys.stderr); sys.exit(1)
    print("\n✅ Done.")

if __name__ == "__main__":
    main()
