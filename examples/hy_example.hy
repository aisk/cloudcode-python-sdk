(import cloudcode)

(defn app [environ start_response]
  (start_response "200 OK" [(, "Content-Type" "text/plain")])
  [(str "Hello LeanCloud!")])

(defn add [params]
  (+ (get params "x") (get params "y")))

(cloudcode.register_cloud_func add)

(defn before_album_save[obj]
  ("ok"))

((cloudcode.register_cloud_hook "Album" "before_save") before_album_save)

(setv app (cloudcode.wrap app))

(defmain [&rest args]
  (cloudcode.run "localhost" 5000 app))
