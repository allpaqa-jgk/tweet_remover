# tweet_remover

古いツイート/リツイートを自動で削除/解除するバッチ機能を提供する小さなツール群です。  
このリポジトリでは、TwitterのAPI設定やユーザーID、GithubのアクセストークンなどをGithub Secretsとして保存し、Github Actionsから定期的に実行します

## 目次
- 概要
- 特長
- 必要条件
- セットアップ（ローカル）
- 環境変数（.env）
- 使い方（実行例）
- アーキテクチャ（簡易）
- 運用上の注意（必読）
- テスト
- 貢献
- ライセンス

---

## 概要
- 定期的に／手動で実行するバッチタスクを実装するための基盤を提供します。

## 特長
- Config / State / Util / Batch / Task / Client の責務分離を想定した構成

## 必要条件
- Python 3.12
- 依存パッケージは `requirements.lock` を参照

## セットアップ（ローカル）
1. リポジトリをクローン
  - git clone https://github.com/allpaqa-jgk/tweet_remover.git
2. Devcontainer 作成、起動(パッケージインストール)
3. 環境変数を準備
  - cp .env.sample .env
  - `.env` を編集して API キー等を設定
4. Secrets の設定
  - `python setup_secrets.py` を実行して Github Secrets / Variables に登録

Devcontainer 以外での動作は未検証なため、問題が発生しても自己責任で対処できる方以外は Devcontainer を利用してください。

## パッケージの追加 / 更新

- `requirements.txt` に追加したいパッケージを追記
- `pip install -r requirements.txt` でインストール
- `pip freeze > requirements.lock` で `requirements.lock` を更新

## 環境変数
.env.sample を元に、少なくとも以下を設定してください。

- GH_TOKEN=repo, workflow 権限を持つ Github Access Token
- X_CLIENT_ID=X アプリのクライアントID
- X_CLIENT_SECRET=X アプリのクライアントシークレット
- X_CUTOFF_DAYS=何日前までのツイートを削除するか
- WEBHOOK_URL=Discord 通知用の Webhook URL

## 使い方
- ローカルで手動実行
  - `python setup_secrets.py` : Github Secrets / Variables の設定, Refresh Token の取得
- Github Actions での定期実行
  - `Fetch and Remove Tweets`
    - 毎日実行
    - キャッシュしたツイート情報が 100 件以下の場合に Twitter API から指定日以前のツイートを取得
    - ツイート情報を元に、指定日数以前のツイートを削除
    - キャッシュ更新
  - `Remove Retweets`
    - 毎時実行
    - キャッシュしたツイート情報を元に、指定日数以前のリツイートを解除
    - キャッシュ更新


## ライセンス
- MIT License（LICENSE ファイルを参照）
