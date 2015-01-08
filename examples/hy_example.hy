(import cloudcode)
(import [werkzeug.serving :as serving])

(defn app [environ start_response]
  (start_response "200 OK" [(, "Content-Type" "text/plain")])
  [(str "Hello LeanCloud!")])

(defn add [params]
  (+ (get params "x") (get params "y")))

(cloudcode.register_cloud_func add)

(setv app (cloudcode.wrap app))

(defmain [&rest args]
  (serving.run_simple "localhost" 5000 app))
