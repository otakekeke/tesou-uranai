import google.generativeai as genai
import PIL.Image
import os
import sys
from dotenv import load_dotenv
import re

def format_diagnosis_to_html(diagnosis_text: str) -> str:
    """
    手相診断結果のテキストを基本的なHTML形式に整形する。
    Markdownの箇条書き(-, *)や太字(**)をHTMLに変換する。

    Args:
        diagnosis_text: 手相診断結果の生テキスト。

    Returns:
        HTML形式に整形されたテキスト。
    """
    lines = diagnosis_text.strip().split('\n')
    html_lines = []
    in_list = False

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue

        # Markdown太字の変換
        processed_line = stripped_line
        processed_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', processed_line)

        if processed_line.startswith('- ') or processed_line.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            # リスト記号とそれに続くスペースを取り除く
            list_item_content = processed_line[2:].strip()
            html_lines.append(f'<li>{list_item_content}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<p>{processed_line}</p>')

    if in_list:
        html_lines.append('</ul>')

    return '\n'.join(html_lines)

def diagnose_and_generate_html(
    image_path: str,
    user_name: str,
    output_html_path: str,
):
    """
    手相画像を診断し、結果を基にHTMLファイルを生成する。

    Args:
        image_path: 手相画像ファイルのパス。
        user_name: 診断対象のユーザー名。
        output_html_path: 出力するHTMLファイルのパス。
    """
    # .envファイルから環境変数を読み込む
    load_dotenv()

    # Google API Keyの設定 (環境変数から読み込む)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
        sys.exit(1)

    genai.configure(api_key=api_key)

    # Gemini Visionモデルをロード
    # 手相診断は画像を含むため vision モデルを使用
    model_vision = genai.GenerativeModel('gemini-2.5-flash-preview-04-17') # response_mime_type はここでは指定しない

    # 手相診断プロンプト
    diagnosis_prompt = """
この手相画像を専門家のように詳細に分析し、手相占いとして以下の情報を提供してください。専門家が見ても違和感がなく、ユーザーが深く納得できるような、根拠に基づいた具体的な洞察とアドバイスを含めてください。結果のテキストのみを出力し、余分な前置きや結びの言葉は一切含めないでください。Markdown形式（箇条書き、太字など）を使用して構造化してください。

分析対象：
- 感情線、頭脳線、生命線など、主要な手相線とその特徴
- その他の重要な線や丘、マーク

提供情報：
- 性格、才能、適性に関する詳細な分析
- 強み、弱み、潜在能力
- 全体的な運勢の傾向（今後の流れ、チャンス、注意点など）
- 健康運、仕事運、恋愛運など、特定の側面に関する具体的な占い
- 運気を向上させるための具体的なアドバイスや行動指針

表現は、専門的でありながらも分かりやすく、ユーザーにとって前向きな内容となるようにしてください。
"""

    # 画像の読み込み
    try:
        img = PIL.Image.open(image_path)
    except FileNotFoundError:
        print(f"エラー: 画像ファイルが見つかりません: {image_path}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: 画像ファイルの読み込み中にエラーが発生しました: {e}")
        sys.exit(1)

    # 手相診断の実行
    print("手相診断を実行中...")
    try:
        # 画像とプロンプトを Vision モデルに送信
        diagnosis_response = model_vision.generate_content([diagnosis_prompt, img])
        diagnosis_result = diagnosis_response.text.strip()
        print("手相診断結果を取得しました。")
        print("--- 診断結果テキスト（Raw）---")
        print(diagnosis_result)
        print("----------------------------")

    except Exception as e:
        print(f"エラー: 手相診断APIの呼び出し中にエラーが発生しました: {e}")
        sys.exit(1)

    # 診断結果をHTML形式に整形
    html_formatted_diagnosis = format_diagnosis_to_html(diagnosis_result)
    print("診断結果テキストをHTML形式に整形しました。")
    print("--- 診断結果テキスト（HTML整形後）---")
    print(html_formatted_diagnosis)
    print("-----------------------------------")


    # Pythonで定義したHTMLテンプレート
    # プレースホルダーを __USER_NAME__ と __DIAGNOSIS_RESULT__ に変更
    # CSSとJavaScript内の波括弧はエスケープしない
    html_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>手相占い結果</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .card-gradient {
            background: linear-gradient(to right, #ffffff, #f7f7f7);
        }
        /* prose クラス内のリストのマーカー色をTailwindのprimaryカラーに合わせる（任意） */
        .prose ul li::before {
             background-color: #667eea; /* Tailwind indigo-500 のような色 */
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen font-sans">
    <!-- ヘッダー部分 - グラデーション背景 -->
    <div class="gradient-bg text-white py-12 shadow-lg mb-8">
        <div class="container mx-auto px-4">
            <h1 class="text-4xl md:text-5xl font-bold text-center mb-4">✨ 手相占い結果 ✨</h1>
            <p class="text-xl text-center opacity-90">あなたの手相が語る運命の道筋</p>
        </div>
    </div>

    <div class="container mx-auto px-4 pb-12">
        <!-- ユーザー情報カード -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8 transform hover:scale-[1.01] transition-transform duration-300 border-l-4 border-indigo-500">
            <div class="flex items-center">
                <div class="bg-indigo-100 p-3 rounded-full mr-4">
                    <i class="fas fa-user text-indigo-600 text-xl"></i>
                </div>
                <div>
                    <h2 class="text-sm uppercase tracking-wider text-gray-500 font-semibold">ユーザー</h2>
                    <p class="text-2xl font-bold text-gray-800">__USER_NAME__</p>
                </div>
            </div>
        </div>

        <!-- 占い結果メインコンテンツ -->
        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
            <!-- ヘッダー -->
            <div class="bg-indigo-600 px-6 py-4">
                <h2 class="text-xl md:text-2xl font-bold text-white">
                    <i class="fas fa-hand-sparkles mr-2"></i>あなたの手相が示す運命
                </h2>
            </div>

            <!-- 占い結果のコンテンツ -->
            <div class="p-6 md:p-8 text-gray-700 leading-relaxed">
                <div class="prose prose-indigo max-w-none">
                    __DIAGNOSIS_RESULT__
                </div>
            </div>

            <!-- フッター -->
            <div class="card-gradient px-6 py-4 border-t border-gray-200">
                <p class="text-gray-600 text-sm italic">
                    <i class="fas fa-info-circle mr-1"></i> この占い結果は、あなたの手相に基づいて生成されたものです。
                    この結果は、提供された画像に基づいてAIが生成したものであり、その正確性や完全性を保証するものではありません。あくまで参考としてお楽しみください。
                    免責事項：本サービスは娯楽目的であり、専門的な手相鑑定やアドバイスに代わるものではありません。
                </p>
            </div>
        </div>

        <!-- 日付表示 -->
        <div class="mt-6 text-center text-gray-500 text-sm">
            <p>鑑定日: <span id="current-date"></span></p>
        </div>
    </div>

    <!-- 日付を設定するスクリプト -->
    <script>
        document.getElementById('current-date').textContent = new Date().toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    </script>
</body>
</html>
"""

    # HTMLテンプレートに値を埋め込み (replaceを使用)
    html_content = html_template.replace('__USER_NAME__', user_name).replace('__DIAGNOSIS_RESULT__', html_formatted_diagnosis)
    print("HTMLテンプレートに値を埋め込みました (replace使用)。")

    # HTMLファイルの保存
    try:
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTMLファイルを保存しました: {output_html_path}")

    except IOError as e:
        print(f"エラー: HTMLファイルの書き込み中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("使用法: python diagnose_and_generate_html.py <画像ファイルパス> <ユーザー名> <出力HTMLファイルパス>")
        sys.exit(1)

    image_path = sys.argv[1]
    user_name = sys.argv[2]
    output_html_path = sys.argv[3]

    diagnose_and_generate_html(image_path, user_name, output_html_path) 