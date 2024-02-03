import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

conn = psycopg2.connect(
        host="localhost",
        database="dedrpg",
        user="postgres",
        password="5152103",
        port = "5432")


cur = conn.cursor()
cur.execute('select * from personagem')
dados = cur.fetchall()

@app.route('/')
def index():
    return render_template('index.html', dados=dados)

#Rota para tela de criação e controle de personagem
@app.route('/creation', methods=('GET', 'POST'))
def creation():
    cur.execute('SELECT * FROM personagem')
    dadospersonagem = cur.fetchall()
    cur.execute('SELECT * FROM  atributos')
    dadosatributos = cur.fetchall()
    
    if request.method == 'POST':
        id = request.form['id']
        nome = request.form['nome']
        raca = request.form['raca']
        ac= int(request.form['ac'])
        nivel = int(request.form['nivel'])
        classe = request.form['classe']
        subclasse = request.form['subclasse']
        cur.execute('INSERT INTO personagem (identificador, nome, raca, ac, nivel, classe, subclasse)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (id, nome, raca, ac, nivel, classe, subclasse))
        conn.commit()
        cur.execute('INSERT INTO atributos (idfk)'
                    'VALUES (%s)',
                    (id,))
        conn.commit()
        return redirect(url_for('creation'))
    return render_template('creation.html', dadospersonagem=dadospersonagem, dadosatributos=dadosatributos, )

#Rota para tela de cadastro e controle de missoes  
@app.route('/mission', methods=('GET', 'POST'))
def mission():
    cur.execute('SELECT * FROM missao')
    dadosmissao = cur.fetchall()
    cur.execute('''
        SELECT P.nome AS nome_personagem, STRING_AGG(M.nome, ', ') AS missoes_concluidas
        FROM concluiu C
        JOIN personagem P ON P.identificador = C.fk_id_personagem
        JOIN missao M ON M.id_mission = C.fk_id_mission
        GROUP BY P.nome
    ''')
    dadosconcluiu= cur.fetchall()
    print(dadosconcluiu)
    
    if 'cadmission' in request.form:
        id_mission = request.form['id_mission']
        nome = request.form['nome']
        recompensa = request.form['recompensa']
        cur.execute('INSERT INTO missao (id_mission, nome, recompensa)'
                    'VALUES (%s, %s, %s)',
                    (id_mission, nome, recompensa))
        conn.commit()
        return redirect(url_for('mission'))
    elif 'cadconcluiu' in request.form:
        fk_id_personagem = request.form['fk_id_personagem']
        fk_id_mission = request.form['fk_id_mission']
        
        cur.execute('INSERT INTO concluiu (fk_id_personagem,fk_id_mission)'
                    'VALUES (%s, %s)',
                    (fk_id_personagem,fk_id_mission))
        conn.commit()
        return redirect(url_for('mission'))
    
    elif 'delconcluiu' in request.form:
        fk_id_personagem = request.form['fk_id_personagem']
        fk_id_mission = request.form['fk_id_mission']
        
        cur.execute('DELETE FROM concluiu WHERE fk_id_personagem = %s and fk_id_mission = %s', (fk_id_personagem, fk_id_mission,))
        conn.commit()
        return redirect(url_for('mission'))

    return render_template('mission.html', dadosmissao=dadosmissao, dadosconcluiu=dadosconcluiu, )
    
    
#Funções e rotas para deletar algo das tabelas
@app.route('/deletarpersonagem/<identificador>')
def deletepersonagem(identificador):
    cur.execute('DELETE FROM personagem WHERE identificador = %s', (identificador,))
    conn.commit()
    return redirect(url_for('creation'))

@app.route('/deletaratributo/<identificador>')
def deleteatributo(identificador):
    cur.execute('DELETE FROM atributos WHERE idfk = %s', (identificador,))
    conn.commit()
    return redirect(url_for('creation'))

@app.route('/deletarmissao/<id_mission>')
def deletemissao(id_mission):
    cur.execute('DELETE FROM missao WHERE id_mission = %s', (id_mission,))
    conn.commit()
    return redirect(url_for('mission'))

@app.route('/updatepersonagem/<identificador>', methods=('GET', 'POST'))
def updatepersonagem(identificador):
    cur.execute('SELECT * FROM personagem WHERE identificador = %s', (identificador,))
    dadospersonagem = cur.fetchall()
    cur.execute('SELECT * FROM atributos WHERE idfk = %s', (identificador,))
    dadosatributos = cur.fetchall()
    if 'attpersonagem' in request.form:

        id = int(request.form['id'])
        nome = request.form['nome']
        raca = request.form['raca']
        ac= int(request.form['ac'])
        nivel = int(request.form['nivel'])
        classe = request.form['classe']
        subclasse = request.form['subclasse']

        cur.execute('UPDATE personagem SET identificador = %s, nome = %s, raca = %s, ac = %s, nivel = %s, classe = %s, subclasse = %s WHERE identificador = %s', (id, nome, raca, ac, nivel, classe, subclasse, identificador))
        conn.commit()
        return redirect(url_for('updatepersonagem', identificador=id))
    
    elif 'attatributos' in request.form:

        forca = int(request.form['forca'])
        destreza = int(request.form['destreza'])
        constituicao= int(request.form['constituicao'])
        sabedoria = int(request.form['sabedoria'])
        inteligencia = int(request.form['inteligencia'])
        carisma = int(request.form['carisma'])

        cur.execute('UPDATE atributos SET forca = %s, destreza = %s, constituicao = %s, sabedoria = %s, inteligencia = %s, carisma = %s WHERE idfk = %s', (forca, destreza, constituicao, sabedoria, inteligencia, carisma, identificador))
        conn.commit()
        return redirect(url_for('updatepersonagem', identificador=identificador))
    return render_template('updatepersonagem.html', dadospersonagem=dadospersonagem, dadosatributos=dadosatributos)

@app.route('/updatemission/<id_mission>', methods=('GET', 'POST'))
def updatemission(id_mission):
    cur.execute('SELECT * FROM missao WHERE id_mission = %s', (id_mission,))
    dadosmissao= cur.fetchall()
    
    if 'attmission' in request.form:

        id = int(request.form['id_mission'])
        nome = request.form['nome']
        recompensa = request.form['recompensa']
        cur.execute('UPDATE missao SET id_mission = %s, nome = %s, recompensa = %s WHERE id_mission = %s', (id, nome, recompensa, id_mission))
        conn.commit()
        return redirect(url_for('updatemission', id_mission = id))
    
    return render_template('updatemission.html', dadosmissao=dadosmissao)


if __name__ == '__main__':
    app.run(debug=True)