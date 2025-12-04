# check links
import json, sqlite3

def check_links(email, con=None):
    # establish connection
    if con is None:
        con = sqlite3.connect('phish.db')
    cur = con.cursor()

    # grab links from email
    # is email given as json or dict?
    try:
        d = json.loads(email)
        links =  d['links']
    except ValueError:
        links = email['links']

    if len(links) < 1:
        return 0, ['no links in email']

    # check links against db for specific URL matches
    urls = [link['url'] for link in links]
    query = f'''SELECT links.url, 
                       links.reputation_score AS link_rep, 
                       links.notes AS link_notes, 
                       domains.domain, 
                       domains.reputation_score AS domain_rep, 
                       domains.notes AS domain_notes
                FROM links LEFT JOIN domains ON links.domain_id = domains.id
                WHERE links.url IN ({', '.join(['?' for _ in urls])})'''
    cur.execute(query, urls)
    records = cur.fetchall()
    score = 0
    notes = []
    for record in records:
        if record[1] is not None:
            note = ''
            for i in range(len(links)):
                if links[i]['url'] == record[0]:
                    link = links.pop(i)

                    if link.get('mismatch'):
                        note += f'Link display text <{link['display_text']}> does not match URL {link['url']}. '

                    note += f'URL {record[0]} has a known reputation score of {record[1]}{f': {record[2]}' if record[2] else ''}. '

                    if record[3] is not None and record[4] is not None:
                        note += f'The link domain, {record[3]}, has a known reputation score of {record[4]}{f': {record[5]}' if record[5] else ''}.'

                    score = max(score, record[1], record[4] if record[4] is not None else 0)
                    notes.append(note.strip())
                    break

    # check remaining links against db for general domain matches
    doms = [link['domain'] for link in links]
    query = f'SELECT domain, reputation_score, notes FROM domains WHERE domain IN ({', '.join(['?' for _ in doms])})'
    cur.execute(query, doms)
    records = cur.fetchall()
    for record in records:
        if record[1] is not None:
            score = max(score, record[1])
            note = f'The domain {record[0]} has a known reputation score of {record[1]}{f': {record[2]}' if record[2] else ''}, and exists in the following URL(s): '
            i = 0
            while i < len(links):
                if links[i]['domain'] == record[0]:
                    link = links.pop(i)
                    note += f'{link['url']}{f' (URL does not match its display text of <{link['display_text']}>)' if link.get('mismatch') else ''}, '
                else:
                    i += 1
            notes.append(note[:-2])

    if len(notes) < 1:
        return 0, ['no familiar links in email']
    return score, notes
