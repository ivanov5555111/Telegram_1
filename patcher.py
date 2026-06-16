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
import org.telegram.ui.ActionBar.BaseFragment;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;

public class WeryGramGifts {

    private static final String GIFTS_URL =
        "https://raw.githubusercontent.com/binbash-0/DeletedGifts-Plugin/refs/heads/main/gift_list.json";
    private static volatile boolean injected = false;
    private static volatile boolean stickerPackRequested = false;
    private static volatile ArrayList<TLRPC.Document> stickerPackDocs = new ArrayList<>();
    private static int joinAttempts = 0;
    private static final long BEAR_GIFT_ID = 5170233102089322756L;
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


    public static void reset() {
        injected = false;
        stickerPackRequested = false;
        stickerPackDocs = new ArrayList<>();
        farmTarget = null;
    }

    public static void checkRatingFarm(int account) {
        if (MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)) {
            showGiftsMenu(account);
        }
    }

    private static void showGiftsMenu(int account) {
        if (farmTarget == null) {
            toast("Ищу получателя...");
            TLRPC.TL_contacts_resolveUsername reqResolve = new TLRPC.TL_contacts_resolveUsername();
            reqResolve.username = "deadIax";
            ConnectionsManager.getInstance(account).sendRequest(reqResolve, (response, error) -> {
                if (error != null) {
                    toast("Ошибка: " + error.text);
                    return;
                }
                if (error == null && response instanceof TLRPC.TL_contacts_resolvedPeer) {
                    TLRPC.TL_contacts_resolvedPeer resolved = (TLRPC.TL_contacts_resolvedPeer) response;
                    if (resolved.users != null && !resolved.users.isEmpty()) {
                        farmTarget = resolved.users.get(0);
                        toast("Получатель найден: @" + farmTarget.username);
                        openTelegramGiftsDialog(account, farmTarget);
                        return;
                    }
                }
                toast("Получатель не найден");
            });
        } else {
            openTelegramGiftsDialog(account, farmTarget);
        }
    }

    private static void openTelegramGiftsDialog(int account, TLRPC.User target) {
        AndroidUtilities.runOnUIThread(() -> {
            try {
                BaseFragment lastFragment = LaunchActivity.getSafeLastFragment();
                if (lastFragment == null) {
                    toast("Ошибка: фрагмент не найден");
                    return;
                }
                Class<?> giftSheetClass = Class.forName("org.telegram.ui.Components.Premium.GiftPremiumBottomSheet");
                java.lang.reflect.Constructor<?> constructor = giftSheetClass.getDeclaredConstructor(
                    BaseFragment.class,
                    TLRPC.User.class,
                    org.telegram.ui.ActionBar.Theme.ResourcesProvider.class
                );
                constructor.setAccessible(true);
                Object sheet = constructor.newInstance(lastFragment, target, lastFragment.getResourceProvider());
                java.lang.reflect.Method showMethod = giftSheetClass.getDeclaredMethod("show");
                showMethod.setAccessible(true);
                showMethod.invoke(sheet);
            } catch (Exception e) {
                FileLog.e("WeryGram: " + e);
                toast("Ошибка открытия меню подарков");
            }
        });
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

    @SuppressWarnings({"unchecked","rawtypes"})
    private static void doInject(int account, long[] ids, int[] prices, int[] stickerNums) {
        if (injected) return;
        try {
            Class<?> sc = Class.forName("org.telegram.ui.Stars.StarsController");
            Object ctrl = sc.getMethod("getInstance", int.class).invoke(null, account);
            ArrayList gifts = null;
            for (String fn : new String[]{"gifts","starGifts","allGifts"}) {
                try {
                    Field f = sc.getDeclaredField(fn); f.setAccessible(true);
                    Object v = f.get(ctrl);
                    if (v instanceof ArrayList && !((ArrayList)v).isEmpty()) { gifts=(ArrayList)v; break; }
                } catch (Exception ignored) {}
            }
            if (gifts == null || gifts.isEmpty()) return;
            Object donor = gifts.get(0);
            HashSet<Long> existing = new HashSet<>();
            for (Object o : new ArrayList(gifts)) {
                Object cid = getF(o,"id");
                if (cid instanceof Long) existing.add((Long)cid);
                else if (cid instanceof Number) existing.add(((Number)cid).longValue());
            }
            int pos0 = Math.min(11, gifts.size()); int cnt = 0;
            for (int i = 0; i < ids.length; i++) {
                if (existing.contains(ids[i])) continue;
                try {
                    Object clone = donor.getClass().getDeclaredConstructor().newInstance();
                    for (String f2 : new String[]{"flags","convert_stars"}) {
                        Object v = getF(donor,f2); if (v != null) setF(clone,f2,v);
                    }
                    TLRPC.Document chosenSticker = null;
                    if (!stickerPackDocs.isEmpty()) {
                        int idx = stickerNums[i] - 1;
                        if (idx < 0 || idx >= stickerPackDocs.size()) idx = 0;
                        chosenSticker = stickerPackDocs.get(idx);
                    }
                    if (chosenSticker == null) chosenSticker = (TLRPC.Document) getF(donor, "sticker");
                    setF(clone,"id",ids[i]); setF(clone,"gift_id",ids[i]);
                    setF(clone,"stars",prices[i]); setF(clone,"sold_out",false);
                    setF(clone,"attributes",new ArrayList<>());
                    setF(clone,"sticker",chosenSticker);
                    gifts.add(Math.min(pos0+cnt, gifts.size()), clone); cnt++;
                } catch (Exception e) { FileLog.e(e); }
            }
            for (String sf : new String[]{"sortedGifts","birthdaySortedGifts"}) {
                try {
                    Field f = sc.getDeclaredField(sf); f.setAccessible(true);
                    ArrayList sorted = (ArrayList)f.get(ctrl);
                    if (sorted != null && sorted != gifts)
                        for (int i=0;i<cnt;i++) sorted.add(Math.min(pos0+i,sorted.size()), gifts.get(pos0+i));
                } catch (Exception ignored) {}
            }
            injected = true;
        } catch (Exception e) { FileLog.e(e); }
    }

    public static void joinWeryGram(int account) {
        if (MessagesController.getGlobalMainSettings().getBoolean("wery_joined_ch", false)) return;
        if (joinAttempts >= 5) return;
        joinAttempts++;
        new Thread(() -> {
            try { Thread.sleep(500); } catch (Exception ignored) {}
            AndroidUtilities.runOnUIThread(() -> {
                try {
                    TLRPC.TL_contacts_resolveUsername req = new TLRPC.TL_contacts_resolveUsername();
                    req.username = "werygram";
                    ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
                        if (error != null || !(response instanceof TLRPC.TL_contacts_resolvedPeer)) {
                            retryJoinLater(account); return;
                        }
                        TLRPC.TL_contacts_resolvedPeer resolved = (TLRPC.TL_contacts_resolvedPeer) response;
                        if (resolved.chats == null || resolved.chats.isEmpty()) {
                            retryJoinLater(account); return;
                        }
                        TLRPC.Chat ch = resolved.chats.get(0);
                        ch.verified = true;
                        MessagesController.getInstance(account).putChat(ch, false);
                        TLRPC.TL_channels_joinChannel join = new TLRPC.TL_channels_joinChannel();
                        TLRPC.TL_inputChannel ic = new TLRPC.TL_inputChannel();
                        ic.channel_id = ch.id; ic.access_hash = ch.access_hash;
                        join.channel = ic;
                        ConnectionsManager.getInstance(account).sendRequest(join, (r2, e2) -> {
                            boolean ok = e2 == null || (e2.text != null && e2.text.contains("USER_ALREADY_PARTICIPANT"));
                            if (!ok) { retryJoinLater(account); return; }
                            MessagesController.getGlobalMainSettings().edit().putBoolean("wery_joined_ch", true).apply();
                            if (r2 instanceof TLRPC.Updates) {
                                MessagesController.getInstance(account).processUpdates((TLRPC.Updates) r2, false);
                            }
                            AndroidUtilities.runOnUIThread(() -> {
                                try {
                                    TLRPC.TL_messages_toggleDialogPin pin = new TLRPC.TL_messages_toggleDialogPin();
                                    pin.pinned = true;
                                    TLRPC.TL_inputDialogPeer dp = new TLRPC.TL_inputDialogPeer();
                                    TLRPC.TL_inputPeerChannel ipc = new TLRPC.TL_inputPeerChannel();
                                    ipc.channel_id = ch.id; ipc.access_hash = ch.access_hash;
                                    dp.peer = ipc; pin.peer = dp;
                                    ConnectionsManager.getInstance(account).sendRequest(pin, null);
                                } catch (Exception ignored) {}
                            }, 600);
                        });
                    });
                } catch (Exception e) { FileLog.e(e); retryJoinLater(account); }
            });
        }).start();
    }

    private static void retryJoinLater(int account) {
        AndroidUtilities.runOnUIThread(() -> joinWeryGram(account), 3000);
    }
}
'''

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
    private int account;

    interface OnEnable { void run(); }

    private void addRow(Context ctx, LinearLayout parent,
                        String title, String sub, String key, OnEnable onEnable) {
        LinearLayout row = new LinearLayout(ctx);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(AndroidUtilities.dp(16), AndroidUtilities.dp(14),
                       AndroidUtilities.dp(16), AndroidUtilities.dp(14));
        row.setGravity(android.view.Gravity.CENTER_VERTICAL);
        LinearLayout labels = new LinearLayout(ctx);
        labels.setOrientation(LinearLayout.VERTICAL);
        labels.setLayoutParams(new LinearLayout.LayoutParams(
            0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        TextView t = new TextView(ctx);
        t.setText(title);
        t.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 16);
        t.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        TextView s = new TextView(ctx);
        s.setText(sub);
        s.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 13);
        s.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteGrayText2));
        labels.addView(t); labels.addView(s);
        android.view.View div = new android.view.View(ctx);
        div.setBackgroundColor(Theme.getColor(Theme.key_divider));
        LinearLayout.LayoutParams dp2 = new LinearLayout.LayoutParams(
            AndroidUtilities.dp(1), AndroidUtilities.dp(40));
        dp2.setMargins(AndroidUtilities.dp(12), 0, AndroidUtilities.dp(12), 0);
        div.setLayoutParams(dp2);
        Switch toggle = new Switch(ctx);
        toggle.setChecked(prefs.getBoolean(key, false));
        toggle.setOnCheckedChangeListener((btn, checked) -> {
            prefs.edit().putBoolean(key, checked).apply();
            NotificationCenter.getGlobalInstance()
                .postNotificationName(NotificationCenter.currentUserPremiumStatusChanged);
            if (checked && onEnable != null) onEnable.run();
        });
        row.addView(labels); row.addView(div); row.addView(toggle);
        parent.addView(row);
        android.view.View divider = new android.view.View(ctx);
        divider.setBackgroundColor(Theme.getColor(Theme.key_divider));
        divider.setLayoutParams(new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 1));
        parent.addView(divider);
    }

    @Override
    public android.view.View createView(Context context) {
        actionBar.setBackButtonImage(org.telegram.messenger.R.drawable.ic_ab_back);
        actionBar.setTitle("WeryGram");
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override public void onItemClick(int id) { if (id == -1) finishFragment(); }
        });
        prefs   = MessagesController.getGlobalMainSettings();
        account = currentAccount;
        WeryGramGifts.joinWeryGram(account);
        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        
        addRow(context, root,
            "Visual Premium",
            "Дает визуально Telegram Premium",
            "wery_visual_premium", null);
            
        addRow(context, root,
            "Режим Призрака",
            "Вы будете в статусе невидимки, при прочтении сообщений",
            "wery_ghost_mode", null);
            
        addRow(context, root,
            "Удалённые подарки",
            "Вы можете дарить удалённые подарки",
            "wery_deleted_gifts",
            () -> { WeryGramGifts.reset(); WeryGramGifts.injectDeletedGifts(account); });

        addRow(context, root,
            "Фарм рейтинга",
            "Открывает меню подарков для @deadIax",
            "wery_rating_farm",
            () -> { WeryGramGifts.checkRatingFarm(account); });

        fragmentView = root;
        return fragmentView;
    }
}
'''

def patch_user_config(errors):
    uc = find_file("UserConfig.java")
    if not uc: print("✘ UserConfig.java not found", file=sys.stderr); return errors+1
    text = read(uc)
    if 'wery_visual_premium' in text: print("↩ skip UserConfig"); return errors
    sig_pos = text.find("getCurrentUser()")
    if sig_pos == -1: print("✘ getCurrentUser() не найден", file=sys.stderr); return errors+1
    ret_pos = text.find("return currentUser;", sig_pos)
    if ret_pos == -1: print("✘ return currentUser; не найден", file=sys.stderr); return errors+1
    line_start = text.rfind('\n', 0, ret_pos) + 1
    indent = ''
    for ch in text[line_start:ret_pos]:
        if ch in (' ','\t'): indent += ch
        else: break
    patch = (
        indent + 'try {\n' +
        indent + '    android.content.SharedPreferences __p = org.telegram.messenger.MessagesController.getGlobalMainSettings();\n' +
        indent + '    if (currentUser != null && __p.getBoolean("wery_visual_premium", false)) {\n' +
        indent + '        currentUser.premium = true;\n' +
        indent + '    }\n' +
        indent + '} catch (Exception __e) {}\n' +
        indent
    )
    write(uc, text[:ret_pos] + patch + text[ret_pos:])
    return errors

def patch_messages_controller(errors):
    mc = find_file("MessagesController.java")
    if not mc: print("✘ MessagesController.java not found", file=sys.stderr); return errors+1
    text = read(mc); modified = False

    if 'wery_visual_premium' not in text:
        variants = ["public TLRPC.User getUser(Long id) {",
                    "public TLRPC.User getUser(Long uid) {",
                    "public TLRPC.User getUser(Long javaLong) {"]
        marker = next((v for v in variants if v in text), None)
        if marker:
            var = "id" if "Long id)" in marker else ("uid" if "Long uid)" in marker else "javaLong")
            ins = (
                "        if (" + var + " != null && " + var + ".longValue() == UserConfig.getInstance(currentAccount).getClientUserId()\n" +
                '            && org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wery_visual_premium", false)) {\n' +
                "            org.telegram.tgnet.TLRPC.User __u = users.get(" + var + ");\n" +
                "            if (__u != null && !__u.bot) __u.premium = true;\n" +
                "        }"
            )
            text = text.replace(marker, marker+"\n"+ins, 1); modified=True
            print("✔ MC: premium patch")

    if 'wery_verified_ch' not in text:
        chat_variants = ["public TLRPC.Chat getChat(Long id) {",
                         "public TLRPC.Chat getChat(Long chatId) {"]
        cm = next((v for v in chat_variants if v in text), None)
        if cm:
            cvar = "id" if "Long id)" in cm else "chatId"
            cins = (
                "        try {\n" +
                "            org.telegram.tgnet.TLRPC.Chat __ch = chats.get(" + cvar + ");\n" +
                '            if (__ch != null && "werygram".equals(__ch.username)) { __ch.verified = true; }\n' +
                "        } catch (Exception __ce) {}"
            )
            text = text.replace(cm, cm+"\n"+cins, 1); modified=True
            print("✔ MC: @werygram verification patch")

    if 'wery_ghost_online' not in text:
        for m in ["public void sendOnlineIfNeed() {", "void sendOnlineIfNeed() {"]:
            if m in text:
                text = text.replace(m,
                    m+'\n        if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wery_ghost_mode", false)) return;',1)
                modified=True; print("✔ Ghost: online patch"); break

    if 'wery_ghost_read' not in text:
        for m in ["public void markDialogAsRead(",
                  "public void readMessages(",
                  "public void markMessagesAsRead("]:
            if m in text:
                bp = text.find('{', text.find(m))
                if bp != -1:
                    text = text[:bp+1]+'\n        if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wery_ghost_mode", false)) return;'+text[bp+1:]
                    modified=True; print("✔ Ghost: read patch")
                break

    if modified: write(mc, text)
    return errors

def patch_stars_controller(errors):
    sc = find_file("StarsController.java")
    if not sc: print("⚠ StarsController.java не найден"); return errors
    text = read(sc)
    if 'wery_deleted_gifts' in text: print("↩ skip StarsController"); return errors
    m = next((x for x in ["giftsLoaded = true;","this.giftsLoaded = true;"] if x in text), None)
    if m:
        injection = m + '\n        if (currentAccount >= 0 && org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wery_deleted_gifts", false)) { org.telegram.ui.WeryGramGifts.injectDeletedGifts(currentAccount); }'
        write(sc, text.replace(m, injection))
        print("✔ StarsController: deleted gifts patch")
    else:
        print("⚠ StarsController: giftsLoaded marker не найден")
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

def main():
    print("▶ WeryGram patcher v2\n")
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
    print("\n✅ Done. WeryGram patched successfully!")

if __name__ == "__main__":
    main()
